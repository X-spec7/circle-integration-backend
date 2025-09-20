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
        total_supply: int,
        price_per_token: Decimal
    ) -> Tuple[str, Dict[str, Any]]:
        """Deploy FundraisingToken contract"""
        try:
            # Convert price to wei (18 decimals)
            price_wei = int(price_per_token * Decimal(10**18))
            
            # Prepare constructor arguments
            constructor_args = [
                name,
                symbol,
                18,  # decimals
                total_supply,
                price_wei,
                self.account.address  # owner
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
        target_amount: Decimal,
        price_per_token: Decimal,
        end_date: int,
        min_investment: int = 100,  # $100 minimum
        max_investment: int = 1000000,  # $1M maximum
        claim_delay: int = 7 * 24 * 3600,  # 7 days
        refund_period: int = 30 * 24 * 3600  # 30 days
    ) -> Tuple[str, Dict[str, Any]]:
        """Deploy IEO contract"""
        try:
            # Convert amounts to wei (6 decimals for USDC)
            target_amount_wei = int(target_amount * Decimal(10**6))
            price_wei = int(price_per_token * Decimal(10**6))
            
            # Prepare constructor arguments
            constructor_args = [
                token_address,  # tokenAddress
                self.account.address,  # admin
                claim_delay,  # CLAIM_DELAY
                refund_period,  # REFUND_PERIOD
                min_investment,  # MIN_INVESTMENT
                max_investment,  # MAX_INVESTMENT
                self.account.address,  # businessAdmin
                end_date,  # ieoStartTime
                price_wei,  # minTokenPrice
                price_wei,  # maxTokenPrice
                price_wei,  # lastValidPrice
                3600,  # priceStalenessThreshold (1 hour)
                1000,  # maxPriceDeviation (10%)
                True,  # circuitBreakerEnabled
                False  # circuitBreakerTriggered
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
    
    async def deploy_project_contracts(
        self,
        name: str,
        symbol: str,
        total_supply: int,
        price_per_token: Decimal,
        target_amount: Decimal,
        end_date: int
    ) -> Dict[str, Any]:
        """Deploy all 3 contracts for a project"""
        try:
            logger.info(f"Starting deployment of project contracts for {name}")
            
            # 1. Deploy FundraisingToken
            token_address, token_deployment = await self.deploy_fundraising_token(
                name=name,
                symbol=symbol,
                total_supply=total_supply,
                price_per_token=price_per_token
            )
            
            # 2. Deploy IEO contract
            ieo_address, ieo_deployment = await self.deploy_ieo_contract(
                token_address=token_address,
                target_amount=target_amount,
                price_per_token=price_per_token,
                end_date=end_date
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
            
            logger.info(f"All contracts deployed successfully for project {name}")
            
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
                }
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
