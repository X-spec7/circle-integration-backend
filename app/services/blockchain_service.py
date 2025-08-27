"""
Blockchain Service for deploying and managing smart contracts
"""
import asyncio
import json
import logging
from typing import Dict, Any, Optional, Tuple
from decimal import Decimal
from web3 import Web3
from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3.contract import Contract
from web3.exceptions import ContractLogicError, TransactionNotFound
from app.core.config import settings

# Import compiled contract constants
try:
    from compiled_contracts.contract_constants import (
        SIMPLEERC20_ABI, SIMPLEERC20_BYTECODE,
        SIMPLEESCROW_ABI, SIMPLEESCROW_BYTECODE
    )
except ImportError:
    # Fallback if compiled contracts are not available
    SIMPLEERC20_ABI = []
    SIMPLEERC20_BYTECODE = "0x"
    SIMPLEESCROW_ABI = []
    SIMPLEESCROW_BYTECODE = "0x"

logger = logging.getLogger(__name__)

class BlockchainService:
    """Service for blockchain operations including contract deployment"""
    
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.polygon_rpc_url))
        self.account: LocalAccount = Account.from_key(settings.polygon_private_key)
        self.w3.eth.default_account = self.account.address
        
        # USDC contract address on Polygon mainnet
        self.usdc_address = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
        
        # Track deployment attempts for cleanup
        self.deployment_attempts = []
        
        # USDC ABI (minimal for transfers)
        self.usdc_abi = [
            {
                "constant": False,
                "inputs": [
                    {"name": "_to", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "transfer",
                "outputs": [{"name": "", "type": "bool"}],
                "payable": False,
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "payable": False,
                "stateMutability": "view",
                "type": "function"
            }
        ]
        
        logger.info(f"Blockchain service initialized with address: {self.account.address}")
    
    def get_current_nonce(self) -> int:
        """Get the current nonce for the deployer account"""
        return self.w3.eth.get_transaction_count(self.account.address)
    
    async def wait_for_transaction_confirmation(self, tx_hash: str, max_wait: int = 60) -> Dict[str, Any]:
        """Wait for transaction confirmation with timeout"""
        try:
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=max_wait)
            return {
                'status': tx_receipt.status,
                'block_number': tx_receipt.blockNumber,
                'gas_used': tx_receipt.gasUsed,
                'contract_address': getattr(tx_receipt, 'contractAddress', None)
            }
        except Exception as e:
            logger.error(f"Error waiting for transaction confirmation: {str(e)}")
            raise
    
    async def deploy_with_retry(self, deployment_func, *args, max_retries: int = 3, **kwargs):
        """Deploy contract with retry logic for nonce issues"""
        for attempt in range(max_retries):
            try:
                result = await deployment_func(*args, **kwargs)
                # Track successful deployment
                self.deployment_attempts.append({
                    'type': deployment_func.__name__,
                    'success': True,
                    'result': result,
                    'attempt': attempt + 1
                })
                return result
            except Exception as e:
                error_msg = str(e)
                # Track failed attempt
                self.deployment_attempts.append({
                    'type': deployment_func.__name__,
                    'success': False,
                    'error': error_msg,
                    'attempt': attempt + 1
                })
                
                if "nonce too low" in error_msg.lower() and attempt < max_retries - 1:
                    logger.warning(f"Nonce issue detected, retrying deployment (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(5)  # Wait 5 seconds before retry
                    continue
                else:
                    logger.error(f"Deployment failed after {attempt + 1} attempts: {error_msg}")
                    raise
    
    def get_deployment_history(self) -> list:
        """Get deployment attempt history for debugging"""
        return self.deployment_attempts.copy()
    
    def clear_deployment_history(self):
        """Clear deployment attempt history"""
        self.deployment_attempts.clear()
    
    async def deploy_erc20_token(
        self,
        name: str,
        symbol: str,
        total_supply: int,
        price_per_token: Decimal,
        owner_address: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Deploy ERC20 token contract
        
        Args:
            name: Token name
            symbol: Token symbol
            total_supply: Total token supply
            price_per_token: Price per token in USDC
            owner_address: Address of the project owner (defaults to deployer address)
            
        Returns:
            Tuple of (contract_address, deployment_info)
        """
        try:
            # Use deployer address as owner if not specified
            if owner_address is None:
                owner_address = self.account.address
            
            # Convert price to wei (18 decimals)
            price_wei = int(price_per_token * Decimal('1e18'))
            
            # Use compiled contract bytecode and ABI
            contract_bytecode = SIMPLEERC20_BYTECODE
            contract_abi = SIMPLEERC20_ABI
            
            if not contract_bytecode or contract_bytecode == "0x":
                raise Exception("Contract bytecode not available. Please compile contracts first.")
            
            # Create contract instance
            contract = self.w3.eth.contract(
                abi=contract_abi,
                bytecode=contract_bytecode
            )
            
            # Prepare constructor parameters
            constructor_params = [
                name,
                symbol,
                total_supply,
                price_wei,
                owner_address
            ]
            
            # Get current nonce
            nonce = self.get_current_nonce()
            
            # Build transaction
            transaction = contract.constructor(*constructor_params).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': 3000000,  # Adjust gas limit as needed
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for transaction receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if tx_receipt.status == 1:
                contract_address = tx_receipt.contractAddress
                deployment_info = {
                    'contract_address': contract_address,
                    'transaction_hash': tx_hash.hex(),
                    'block_number': tx_receipt.blockNumber,
                    'gas_used': tx_receipt.gasUsed
                }
                
                logger.info(f"ERC20 token deployed successfully: {contract_address}")
                return contract_address, deployment_info
            else:
                raise Exception("Contract deployment failed")
                
        except Exception as e:
            logger.error(f"Error deploying ERC20 token: {str(e)}")
            raise
    
    async def deploy_escrow_contract(
        self,
        project_token_address: str,
        project_owner_address: str,
        target_amount: Decimal,
        token_price: Decimal,
        end_date: int
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Deploy escrow contract for a project
        
        Args:
            project_token_address: Address of the project's ERC20 token
            project_owner_address: Address of the project owner
            target_amount: Target fundraising amount in USDC
            token_price: Price per token in USDC
            end_date: Project end date as Unix timestamp
            
        Returns:
            Tuple of (contract_address, deployment_info)
        """
        try:
            # Convert amounts to wei (18 decimals)
            target_amount_wei = int(target_amount * Decimal('1e18'))
            token_price_wei = int(token_price * Decimal('1e18'))
            
            # Use compiled contract bytecode and ABI
            contract_bytecode = SIMPLEESCROW_BYTECODE
            contract_abi = SIMPLEESCROW_ABI
            
            if not contract_bytecode or contract_bytecode == "0x":
                raise Exception("Contract bytecode not available. Please compile contracts first.")
            
            # Create contract instance
            contract = self.w3.eth.contract(
                abi=contract_abi,
                bytecode=contract_bytecode
            )
            
            # Prepare constructor parameters
            constructor_params = [
                project_token_address,
                self.usdc_address,  # USDC token address
                project_owner_address,
                target_amount_wei,
                token_price_wei,
                end_date
            ]
            
            # Get current nonce (wait a bit to ensure previous transaction is processed)
            await asyncio.sleep(2)  # Wait 2 seconds for previous transaction
            nonce = self.get_current_nonce()
            
            # Build transaction
            transaction = contract.constructor(*constructor_params).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': 4000000,  # Higher gas limit for escrow contract
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for transaction receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if tx_receipt.status == 1:
                contract_address = tx_receipt.contractAddress
                deployment_info = {
                    'contract_address': contract_address,
                    'transaction_hash': tx_hash.hex(),
                    'block_number': tx_receipt.blockNumber,
                    'gas_used': tx_receipt.gasUsed
                }
                
                logger.info(f"Escrow contract deployed successfully: {contract_address}")
                return contract_address, deployment_info
            else:
                raise Exception("Contract deployment failed")
                
        except Exception as e:
            logger.error(f"Error deploying escrow contract: {str(e)}")
            raise
    
    async def transfer_eurc_to_escrow(
        self,
        escrow_address: str,
        amount: Decimal
    ) -> Dict[str, Any]:
        """
        Transfer EURC tokens to escrow contract
        
        Args:
            escrow_address: Address of the escrow contract
            amount: Amount to transfer in EURC
            
        Returns:
            Transaction information
        """
        try:
            # EURC contract address on Polygon (you'll need to verify this)
            eurc_address = "0xE111178A87A3BFf0c8d18DECBa5798827539Ae99"
            
            # Create EURC contract instance
            eurc_contract = self.w3.eth.contract(
                address=eurc_address,
                abi=self.usdc_abi  # Using same ABI as USDC
            )
            
            # Convert amount to wei (6 decimals for EURC)
            amount_wei = int(amount * Decimal('1e6'))
            
            # Build transfer transaction
            transaction = eurc_contract.functions.transfer(
                escrow_address,
                amount_wei
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for transaction receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if tx_receipt.status == 1:
                transfer_info = {
                    'transaction_hash': tx_hash.hex(),
                    'block_number': tx_receipt.blockNumber,
                    'gas_used': tx_receipt.gasUsed,
                    'amount': amount,
                    'recipient': escrow_address
                }
                
                logger.info(f"EURC transfer successful: {amount} to {escrow_address}")
                return transfer_info
            else:
                raise Exception("EURC transfer failed")
                
        except Exception as e:
            logger.error(f"Error transferring EURC: {str(e)}")
            raise
    
    async def get_contract_balance(self, contract_address: str, token_address: str) -> Decimal:
        """
        Get token balance of a contract
        
        Args:
            contract_address: Address of the contract
            token_address: Address of the token contract
            
        Returns:
            Balance as Decimal
        """
        try:
            token_contract = self.w3.eth.contract(
                address=token_address,
                abi=self.usdc_abi
            )
            
            balance_wei = token_contract.functions.balanceOf(contract_address).call()
            balance = Decimal(balance_wei) / Decimal('1e6')  # Assuming 6 decimals
            
            return balance
            
        except Exception as e:
            logger.error(f"Error getting contract balance: {str(e)}")
            raise
    
    async def get_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        """
        Get transaction status
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            Transaction status information
        """
        try:
            tx_receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            
            if tx_receipt:
                return {
                    'status': 'success' if tx_receipt.status == 1 else 'failed',
                    'block_number': tx_receipt.blockNumber,
                    'gas_used': tx_receipt.gasUsed,
                    'contract_address': tx_receipt.contractAddress
                }
            else:
                return {'status': 'pending'}
                
        except TransactionNotFound:
            return {'status': 'pending'}
        except Exception as e:
            logger.error(f"Error getting transaction status: {str(e)}")
            raise

# Global blockchain service instance
blockchain_service = BlockchainService() 