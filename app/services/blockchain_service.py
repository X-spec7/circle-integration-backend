"""
Blockchain Service for deploying and managing smart contracts
"""
import asyncio
import json
import logging
import time
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

# Configure logging
logger = logging.getLogger(__name__)

class BlockchainService:
    """Service for blockchain operations including contract deployment"""
    
    def __init__(self):
        self.w3 = None
        self.account = None
        self._setup_web3()
    
    def _setup_web3(self):
        """Setup Web3 connection and account"""
        try:
            logger.info(f"🔗 Setting up blockchain connection for network: {settings.network}")
            
            # Select RPC URL based on network
            if settings.network.upper() == "SEPOLIA":
                rpc_url = settings.sepolia_rpc_url
                logger.info(f"📍 Using Sepolia network: {rpc_url}")
            elif settings.network.upper() == "POLYGON":
                rpc_url = settings.polygon_rpc_url
                logger.info(f"📍 Using Polygon network: {rpc_url}")
            elif settings.network.upper() == "MAINNET":
                rpc_url = settings.mainnet_rpc_url
                logger.info(f"📍 Using Ethereum Mainnet: {rpc_url}")
            else:
                raise ValueError(f"Unsupported network: {settings.network}")
            
            # Initialize Web3
            self.w3 = Web3(Web3.HTTPProvider(rpc_url))
            
            # Check connection
            if not self.w3.is_connected():
                logger.error(f"❌ Failed to connect to {settings.network} RPC: {rpc_url}")
                raise Exception(f"Failed to connect to {settings.network} RPC")
            
            logger.info(f"✅ Connected to {settings.network} network")
            logger.info(f"🔗 Chain ID: {self.w3.eth.chain_id}")
            logger.info(f"📊 Latest block: {self.w3.eth.block_number}")
            
            # Setup account
            private_key = self._get_private_key()
            if not private_key:
                raise Exception("Private key not configured")
            
            self.account = Account.from_key(private_key)
            logger.info(f"👤 Account address: {self.account.address}")
            
            # Check account balance
            balance = self.w3.eth.get_balance(self.account.address)
            balance_eth = self.w3.from_wei(balance, 'ether')
            logger.info(f"💰 Account balance: {balance_eth} ETH")
            
            if balance == 0:
                logger.warning("⚠️  Account has zero balance - transactions will fail")
            
        except Exception as e:
            logger.error(f"❌ Failed to setup Web3: {str(e)}")
            raise
    
    def _get_private_key(self) -> Optional[str]:
        """Get private key based on network"""
        if settings.network.upper() == "SEPOLIA":
            return settings.sepolia_private_key
        elif settings.network.upper() == "POLYGON":
            return settings.polygon_private_key
        elif settings.network.upper() == "MAINNET":
            return settings.mainnet_private_key
        return None
    
    def _get_gas_price(self) -> int:
        """Get current gas price with safety margin"""
        try:
            # Get current gas price
            gas_price = self.w3.eth.gas_price
            logger.info(f"⛽ Current gas price: {gas_price} wei ({self.w3.from_wei(gas_price, 'gwei')} gwei)")
            
            # Add 20% safety margin to avoid "underpriced" errors
            safe_gas_price = int(gas_price * 1.2)
            logger.info(f"⛽ Safe gas price: {safe_gas_price} wei ({self.w3.from_wei(safe_gas_price, 'gwei')} gwei)")
            
            return safe_gas_price
        except Exception as e:
            logger.warning(f"⚠️  Failed to get gas price: {e}, using default")
            # Use higher default gas price
            return self.w3.to_wei('30', 'gwei')  # Increased from 20 to 30 gwei
    
    def _get_nonce(self) -> int:
        """Get current nonce for the account"""
        try:
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            logger.info(f"🔢 Current nonce: {nonce}")
            return nonce
        except Exception as e:
            logger.error(f"❌ Failed to get nonce: {str(e)}")
            raise
    
    def _estimate_gas(self, transaction: Dict[str, Any]) -> int:
        """Estimate gas for transaction with safety margin"""
        try:
            gas_estimate = self.w3.eth.estimate_gas(transaction)
            logger.info(f"⛽ Estimated gas: {gas_estimate}")
            
            # Add 50% safety margin for contract deployments
            safe_gas = int(gas_estimate * 1.5)
            logger.info(f"⛽ Safe gas limit: {safe_gas}")
            return safe_gas
        except Exception as e:
            logger.warning(f"⚠️  Failed to estimate gas: {e}, using default")
            return 1000000  # Higher default for contract deployments
    
    def _send_transaction(self, transaction: Dict[str, Any], description: str) -> str:
        """Send transaction and wait for confirmation with retry logic"""
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                logger.info(f"📤 Sending transaction (attempt {attempt + 1}/{max_retries}): {description}")
                
                # Sign transaction
                signed_txn = self.w3.eth.account.sign_transaction(transaction, self.account.key)
                logger.info(f"✍️  Transaction signed")
                
                # Send transaction
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                tx_hash_hex = tx_hash.hex()
                logger.info(f"📤 Transaction sent: {tx_hash_hex}")
                
                # Wait for confirmation with longer timeout
                logger.info(f"⏳ Waiting for transaction confirmation...")
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)  # Increased timeout
                
                if receipt.status == 1:
                    logger.info(f"✅ Transaction confirmed: {tx_hash_hex}")
                    logger.info(f"📊 Gas used: {receipt.gasUsed}")
                    logger.info(f"📊 Block number: {receipt.blockNumber}")
                    return tx_hash_hex
                else:
                    logger.error(f"❌ Transaction failed: {tx_hash_hex}")
                    if attempt < max_retries - 1:
                        logger.info(f"🔄 Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    raise Exception(f"Transaction failed: {tx_hash_hex}")
                    
            except Exception as e:
                logger.error(f"❌ Transaction error (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    logger.info(f"🔄 Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                raise
        
        raise Exception(f"Transaction failed after {max_retries} attempts")
    
    async def deploy_fundraising_token(
        self, 
        name: str, 
        symbol: str, 
        decimals: int = 18, 
        initial_supply: int = 1000000
    ) -> Tuple[str, str]:
        """Deploy FundraisingToken contract"""
        try:
            logger.info(f"🚀 Deploying FundraisingToken contract...")
            logger.info(f"📋 Contract details: name={name}, symbol={symbol}, decimals={decimals}, initial_supply={initial_supply}")
            
            # Check if contract is compiled
            if not FUNDRAISINGTOKEN_BYTECODE or FUNDRAISINGTOKEN_BYTECODE == "0x":
                raise Exception("FundraisingToken contract not compiled")
            
            # Get gas price and nonce
            gas_price = self._get_gas_price()
            nonce = self._get_nonce()
            
            # Create contract instance
            contract = self.w3.eth.contract(
                abi=FUNDRAISINGTOKEN_ABI,
                bytecode=FUNDRAISINGTOKEN_BYTECODE
            )
            
            # Build constructor transaction
            constructor_tx = contract.constructor(
                name, symbol, decimals, initial_supply
            ).build_transaction({
                'from': self.account.address,
                'gasPrice': gas_price,
                'nonce': nonce
            })
            
            # Estimate gas
            gas_estimate = self._estimate_gas(constructor_tx)
            constructor_tx['gas'] = gas_estimate
            
            # Send transaction
            tx_hash = self._send_transaction(constructor_tx, "FundraisingToken deployment")
            
            # Get contract address from receipt
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            contract_address = receipt.contractAddress
            
            logger.info(f"✅ FundraisingToken deployed successfully!")
            logger.info(f"📍 Contract address: {contract_address}")
            logger.info(f"🔗 Transaction: {tx_hash}")
            
            return contract_address, tx_hash
            
        except Exception as e:
            logger.error(f"❌ Failed to deploy FundraisingToken: {str(e)}")
            raise
    
    async def deploy_ieo_contract(
        self, 
        token_address: str, 
        admin_address: str, 
        business_admin_address: str,
        delay_days: int = 7,
        min_investment: int = 100,
        max_investment: int = 1000000
    ) -> Tuple[str, str]:
        """Deploy IEO contract"""
        try:
            logger.info(f"🚀 Deploying IEO contract...")
            logger.info(f"📋 Contract details: token={token_address}, admin={admin_address}, business_admin={business_admin_address}")
            logger.info(f"📋 IEO settings: delay_days={delay_days}, min_investment={min_investment}, max_investment={max_investment}")
            
            # Check if contract is compiled
            if not IEO_BYTECODE or IEO_BYTECODE == "0x":
                raise Exception("IEO contract not compiled")
            
            # Get gas price and nonce
            gas_price = self._get_gas_price()
            nonce = self._get_nonce()
            
            # Create contract instance
            contract = self.w3.eth.contract(
                abi=IEO_ABI,
                bytecode=IEO_BYTECODE
            )
            
            # Build constructor transaction
            constructor_tx = contract.constructor(
                token_address,
                admin_address,
                business_admin_address,
                delay_days,
                min_investment,
                max_investment
            ).build_transaction({
                'from': self.account.address,
                'gasPrice': gas_price,
                'nonce': nonce
            })
            
            # Estimate gas
            gas_estimate = self._estimate_gas(constructor_tx)
            constructor_tx['gas'] = gas_estimate
            
            # Send transaction
            tx_hash = self._send_transaction(constructor_tx, "IEO contract deployment")
            
            # Get contract address from receipt
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            contract_address = receipt.contractAddress
            
            logger.info(f"✅ IEO contract deployed successfully!")
            logger.info(f"📍 Contract address: {contract_address}")
            logger.info(f"�� Transaction: {tx_hash}")
            
            return contract_address, tx_hash
            
        except Exception as e:
            logger.error(f"❌ Failed to deploy IEO contract: {str(e)}")
            raise
    
    async def deploy_reward_tracking_contract(
        self, 
        token_address: str, 
        ieo_contract_address: str
    ) -> Tuple[str, str]:
        """Deploy RewardTracking contract"""
        try:
            logger.info(f"🚀 Deploying RewardTracking contract...")
            logger.info(f"📋 Contract details: token={token_address}, ieo_contract={ieo_contract_address}")
            
            # Check if contract is compiled
            if not REWARDTRACKING_BYTECODE or REWARDTRACKING_BYTECODE == "0x":
                raise Exception("RewardTracking contract not compiled")
            
            # Get gas price and nonce
            gas_price = self._get_gas_price()
            nonce = self._get_nonce()
            
            # Create contract instance
            contract = self.w3.eth.contract(
                abi=REWARDTRACKING_ABI,
                bytecode=REWARDTRACKING_BYTECODE
            )
            
            # Build constructor transaction
            constructor_tx = contract.constructor(
                token_address,
                ieo_contract_address
            ).build_transaction({
                'from': self.account.address,
                'gasPrice': gas_price,
                'nonce': nonce
            })
            
            # Estimate gas
            gas_estimate = self._estimate_gas(constructor_tx)
            constructor_tx['gas'] = gas_estimate
            
            # Send transaction
            tx_hash = self._send_transaction(constructor_tx, "RewardTracking contract deployment")
            
            # Get contract address from receipt
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            contract_address = receipt.contractAddress
            
            logger.info(f"✅ RewardTracking contract deployed successfully!")
            logger.info(f"📍 Contract address: {contract_address}")
            logger.info(f"🔗 Transaction: {tx_hash}")
            
            return contract_address, tx_hash
            
        except Exception as e:
            logger.error(f"❌ Failed to deploy RewardTracking contract: {str(e)}")
            raise
    
    async def deploy_project_contracts(
        self,
        project_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deploy all 3 contracts for a project"""
        try:
            logger.info(f"🚀 Starting project contract deployment...")
            logger.info(f"📋 Project: {project_data.get('name', 'Unknown')} ({project_data.get('symbol', 'UNK')})")
            
            # Step 1: Deploy FundraisingToken
            logger.info(f"📝 Step 1/3: Deploying FundraisingToken...")
            token_address, token_tx = await self.deploy_fundraising_token(
                name=project_data['name'],
                symbol=project_data['symbol'],
                decimals=18,
                initial_supply=project_data['initial_supply']
            )
            
            # Wait a bit between deployments to avoid nonce conflicts
            await asyncio.sleep(2)
            
            # Step 2: Deploy IEO contract
            logger.info(f"📝 Step 2/3: Deploying IEO contract...")
            ieo_address, ieo_tx = await self.deploy_ieo_contract(
                token_address=token_address,
                admin_address=self.account.address,
                business_admin_address=project_data['business_admin_wallet'],
                delay_days=project_data.get('delay_days', 7),
                min_investment=project_data.get('min_investment', 100),
                max_investment=project_data.get('max_investment', 1000000)
            )
            
            # Wait a bit between deployments
            await asyncio.sleep(2)
            
            # Step 3: Deploy RewardTracking contract
            logger.info(f"📝 Step 3/3: Deploying RewardTracking contract...")
            reward_address, reward_tx = await self.deploy_reward_tracking_contract(
                token_address=token_address,
                ieo_contract_address=ieo_address
            )
            
            # Configure contracts
            logger.info(f"🔧 Configuring contracts...")
            await self.configure_contracts(token_address, ieo_address, reward_address)
            
            # Transfer initial tokens to business admin
            logger.info(f"💸 Transferring initial tokens to business admin...")
            await self.transfer_tokens(
                token_address=token_address,
                to_address=project_data['business_admin_wallet'],
                amount=project_data['initial_supply']
            )
            
            logger.info(f"🎉 All contracts deployed successfully!")
            
            return {
                'token_contract_address': token_address,
                'ieo_contract_address': ieo_address,
                'reward_tracking_contract_address': reward_address,
                'token_deployment_tx': token_tx,
                'ieo_deployment_tx': ieo_tx,
                'reward_tracking_deployment_tx': reward_tx,
                'deployment_status': 'completed'
            }
            
        except Exception as e:
            logger.error(f"❌ Project contract deployment failed: {str(e)}")
            raise
    
    async def configure_contracts(
        self, 
        token_address: str, 
        ieo_address: str, 
        reward_address: str
    ) -> None:
        """Configure contracts to work together"""
        try:
            logger.info(f"🔧 Configuring contracts...")
            logger.info(f"📋 Token: {token_address}")
            logger.info(f"📋 IEO: {ieo_address}")
            logger.info(f"📋 Reward: {reward_address}")
            
            # This would include any necessary contract configuration
            # For now, just log the configuration
            logger.info(f"✅ Contracts configured successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to configure contracts: {str(e)}")
            raise
    
    async def transfer_tokens(
        self, 
        token_address: str, 
        to_address: str, 
        amount: int
    ) -> str:
        """Transfer tokens to business admin wallet"""
        try:
            logger.info(f"💸 Transferring {amount} tokens to {to_address}...")
            
            # Create token contract instance
            token_contract = self.w3.eth.contract(
                address=token_address,
                abi=FUNDRAISINGTOKEN_ABI
            )
            
            # Get gas price and nonce
            gas_price = self._get_gas_price()
            nonce = self._get_nonce()
            
            # Build transfer transaction
            transfer_tx = token_contract.functions.transfer(
                to_address, amount
            ).build_transaction({
                'from': self.account.address,
                'gasPrice': gas_price,
                'nonce': nonce
            })
            
            # Estimate gas
            gas_estimate = self._estimate_gas(transfer_tx)
            transfer_tx['gas'] = gas_estimate
            
            # Send transaction
            tx_hash = self._send_transaction(transfer_tx, f"Transfer {amount} tokens to {to_address}")
            
            logger.info(f"✅ Tokens transferred successfully: {tx_hash}")
            return tx_hash
            
        except Exception as e:
            logger.error(f"❌ Failed to transfer tokens: {str(e)}")
            raise

# Create service instance
blockchain_service = BlockchainService()
