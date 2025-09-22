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
        FUNDRAISINGTOKEN_ABI, FUNDRAISINGTOKEN_BYTECODE,
        IEO_ABI, IEO_BYTECODE,
        REWARDTRACKING_ABI, REWARDTRACKING_BYTECODE
    )
except ImportError:
    # Fallback if compiled contracts are not available
    FUNDRAISINGTOKEN_ABI = []
    FUNDRAISINGTOKEN_BYTECODE = "0x"
    IEO_ABI = []
    IEO_BYTECODE = "0x"
    REWARDTRACKING_ABI = []
    REWARDTRACKING_BYTECODE = "0x"

logger = logging.getLogger(__name__)

class BlockchainService:
    """Service for blockchain operations including contract deployment"""
    
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.sepolia_rpc_url))
        self.account: LocalAccount = Account.from_key(settings.sepolia_private_key)
        self.w3.eth.default_account = self.account.address
        
        # Get USDC address based on network
        self.usdc_address = settings.usdc_address
        
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
        
        logger.info(f"Blockchain service initialized with network: {settings.network}")
        logger.info(f"RPC URL: {settings.rpc_url}")
        logger.info(f"Account address: {self.account.address}")
        logger.info(f"USDC address: {self.usdc_address}")
    
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
                logger.warning(f"Deployment attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    # Track failed deployment
                    self.deployment_attempts.append({
                        'type': deployment_func.__name__,
                        'success': False,
                        'error': str(e),
                        'attempt': attempt + 1
                    })
                    raise
                await asyncio.sleep(2)  # Wait before retry
    
    async def deploy_fundraising_token(
        self,
        name: str,
        symbol: str,
        initial_supply: int,
        decimals: int = 18
    ) -> Tuple[str, Dict[str, Any]]:
        """Deploy FundraisingToken contract"""
        try:
            # Prepare constructor arguments
            constructor_args = [
                name,
                symbol,
                decimals,
                initial_supply
            ]
            
            # Deploy contract
            contract = self.w3.eth.contract(
                abi=FUNDRAISINGTOKEN_ABI,
                bytecode=FUNDRAISINGTOKEN_BYTECODE
            )
            
            # Build transaction
            constructor = contract.constructor(*constructor_args)
            tx = constructor.build_transaction({
                'from': self.account.address,
                'nonce': self.get_current_nonce(),
                'gas': 2000000,  # Increased gas limit
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Sign and send transaction
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for confirmation
            tx_receipt = await self.wait_for_transaction_confirmation(tx_hash.hex())
            
            if tx_receipt['status'] == 1:
                contract_address = tx_receipt['contract_address']
                logger.info(f"FundraisingToken deployed at: {contract_address}")
                
                return contract_address, {
                    'transaction_hash': tx_hash.hex(),
                    'contract_address': contract_address,
                    'gas_used': tx_receipt['gas_used'],
                    'block_number': tx_receipt['block_number']
                }
            else:
                raise Exception("Transaction failed")
                
        except Exception as e:
            logger.error(f"Error deploying FundraisingToken: {str(e)}")
            raise
    
    async def deploy_ieo_contract(
        self,
        token_address: str,
        admin_address: str,
        business_admin_address: str,
        delay_days: int = 7,
        min_investment: int = 100,  # $100 minimum in USDC (6 decimals)
        max_investment: int = 1000000  # $1M maximum in USDC (6 decimals)
    ) -> Tuple[str, Dict[str, Any]]:
        """Deploy IEO contract"""
        try:
            # Prepare constructor arguments
            constructor_args = [
                token_address,  # _tokenAddress
                admin_address,  # _admin
                business_admin_address,  # _businessAdmin
                delay_days,  # _delayDays
                min_investment,  # _minInvestment (in USDC, 6 decimals)
                max_investment   # _maxInvestment (in USDC, 6 decimals)
            ]
            
            # Deploy contract
            contract = self.w3.eth.contract(
                abi=IEO_ABI,
                bytecode=IEO_BYTECODE
            )
            
            # Build transaction
            constructor = contract.constructor(*constructor_args)
            tx = constructor.build_transaction({
                'from': self.account.address,
                'nonce': self.get_current_nonce(),
                'gas': 3000000,  # Increased gas limit for IEO
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Sign and send transaction
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for confirmation
            tx_receipt = await self.wait_for_transaction_confirmation(tx_hash.hex())
            
            if tx_receipt['status'] == 1:
                contract_address = tx_receipt['contract_address']
                logger.info(f"IEO contract deployed at: {contract_address}")
                
                return contract_address, {
                    'transaction_hash': tx_hash.hex(),
                    'contract_address': contract_address,
                    'gas_used': tx_receipt['gas_used'],
                    'block_number': tx_receipt['block_number']
                }
            else:
                raise Exception("Transaction failed")
                
        except Exception as e:
            logger.error(f"Error deploying IEO contract: {str(e)}")
            raise
    
    async def deploy_reward_tracking_contract(
        self,
        token_address: str,
        ieo_address: str
    ) -> Tuple[str, Dict[str, Any]]:
        """Deploy RewardTracking contract"""
        try:
            # Prepare constructor arguments
            constructor_args = [
                token_address,  # tokenAddress
                ieo_address    # ieoContract
            ]
            
            # Deploy contract
            contract = self.w3.eth.contract(
                abi=REWARDTRACKING_ABI,
                bytecode=REWARDTRACKING_BYTECODE
            )
            
            # Build transaction
            constructor = contract.constructor(*constructor_args)
            tx = constructor.build_transaction({
                'from': self.account.address,
                'nonce': self.get_current_nonce(),
                'gas': 2000000,  # Gas limit for RewardTracking
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Sign and send transaction
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for confirmation
            tx_receipt = await self.wait_for_transaction_confirmation(tx_hash.hex())
            
            if tx_receipt['status'] == 1:
                contract_address = tx_receipt['contract_address']
                logger.info(f"RewardTracking contract deployed at: {contract_address}")
                
                return contract_address, {
                    'transaction_hash': tx_hash.hex(),
                    'contract_address': contract_address,
                    'gas_used': tx_receipt['gas_used'],
                    'block_number': tx_receipt['block_number']
                }
            else:
                raise Exception("Transaction failed")
                
        except Exception as e:
            logger.error(f"Error deploying RewardTracking contract: {str(e)}")
            raise
    
    async def transfer_tokens_to_business_admin(
        self,
        token_address: str,
        business_admin_address: str,
        amount: int
    ) -> Dict[str, Any]:
        """Transfer tokens from deployer to business admin wallet"""
        try:
            # Get contract instance
            token_contract = self.w3.eth.contract(
                address=token_address,
                abi=FUNDRAISINGTOKEN_ABI
            )
            
            # Build transfer transaction
            tx = token_contract.functions.transfer(
                business_admin_address,
                amount
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.get_current_nonce(),
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Sign and send transaction
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for confirmation
            tx_receipt = await self.wait_for_transaction_confirmation(tx_hash.hex())
            
            if tx_receipt['status'] == 1:
                logger.info(f"Transferred {amount} tokens to business admin: {business_admin_address}")
                
                return {
                    'transaction_hash': tx_hash.hex(),
                    'gas_used': tx_receipt['gas_used'],
                    'block_number': tx_receipt['block_number'],
                    'success': True
                }
            else:
                raise Exception("Token transfer transaction failed")
                
        except Exception as e:
            logger.error(f"Error transferring tokens to business admin: {str(e)}")
            raise
    
    async def deploy_project_contracts(
        self,
        name: str,
        symbol: str,
        initial_supply: int,
        business_admin_address: str,
        delay_days: int = 7,
        min_investment: int = 100,
        max_investment: int = 1000000
    ) -> Dict[str, Any]:
        """Deploy all 3 contracts for a project and transfer tokens to business admin"""
        try:
            logger.info(f"Starting deployment of project contracts for {name}")
            logger.info(f"Business admin address: {business_admin_address}")
            
            # 1. Deploy FundraisingToken
            token_address, token_deployment = await self.deploy_fundraising_token(
                name=name,
                symbol=symbol,
                initial_supply=initial_supply,
                decimals=18
            )
            
            # 2. Deploy IEO contract with business admin address
            ieo_address, ieo_deployment = await self.deploy_ieo_contract(
                token_address=token_address,
                admin_address=self.account.address,  # Platform admin
                business_admin_address=business_admin_address,  # Business admin
                delay_days=delay_days,
                min_investment=min_investment,
                max_investment=max_investment
            )
            
            # 3. Deploy RewardTracking contract
            reward_tracking_address, reward_tracking_deployment = await self.deploy_reward_tracking_contract(
                token_address=token_address,
                ieo_address=ieo_address
            )
            
            # 4. Configure contracts (set reward tracking addresses)
            await self.configure_contracts(
                token_address=token_address,
                ieo_address=ieo_address,
                reward_tracking_address=reward_tracking_address
            )
            
            # 5. Transfer all tokens to business admin wallet
            token_transfer_result = await self.transfer_tokens_to_business_admin(
                token_address=token_address,
                business_admin_address=business_admin_address,
                amount=initial_supply
            )
            
            logger.info(f"All contracts deployed successfully for project {name}")
            logger.info(f"Tokens transferred to business admin: {business_admin_address}")
            
            return {
                'token_contract': {
                    'address': token_address,
                    'deployment': token_deployment
                },
                'ieo_contract': {
                    'address': ieo_address,
                    'deployment': ieo_deployment
                },
                'reward_tracking_contract': {
                    'address': reward_tracking_address,
                    'deployment': reward_tracking_deployment
                },
                'token_transfer': {
                    'transaction_hash': token_transfer_result['transaction_hash'],
                    'gas_used': token_transfer_result['gas_used'],
                    'success': token_transfer_result['success']
                },
                'business_admin_wallet': business_admin_address
            }
            
        except Exception as e:
            logger.error(f"Error deploying project contracts: {str(e)}")
            raise
    
    async def configure_contracts(
        self,
        token_address: str,
        ieo_address: str,
        reward_tracking_address: str
    ):
        """Configure contracts to work together"""
        try:
            # Get contract instances
            token_contract = self.w3.eth.contract(
                address=token_address,
                abi=FUNDRAISINGTOKEN_ABI
            )
            
            ieo_contract = self.w3.eth.contract(
                address=ieo_address,
                abi=IEO_ABI
            )
            
            # Set reward tracking address in token contract
            tx = token_contract.functions.setRewardTrackingAddress(reward_tracking_address).build_transaction({
                'from': self.account.address,
                'nonce': self.get_current_nonce(),
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            await self.wait_for_transaction_confirmation(tx_hash.hex())
            
            # Set reward tracking address in IEO contract
            tx = ieo_contract.functions.setRewardTrackingAddress(reward_tracking_address).build_transaction({
                'from': self.account.address,
                'nonce': self.get_current_nonce(),
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            await self.wait_for_transaction_confirmation(tx_hash.hex())
            
            logger.info("Contracts configured successfully")
            
        except Exception as e:
            logger.error(f"Error configuring contracts: {str(e)}")
            raise

# Global instance
blockchain_service = BlockchainService()
