import asyncio
import logging
from typing import Dict, Any, Optional, Tuple, List
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from app.core.config import settings
from compiled_contracts.contract_constants import (
    FUNDRAISINGTOKEN_ABI,
    FUNDRAISINGTOKEN_BYTECODE,
    IEO_ABI,
    IEO_BYTECODE,
    REWARDTRACKING_ABI,
    MOCKPRICEORACLE_ABI,
    REWARDTRACKING_BYTECODE
)
# Minimal ERC20 interface for decimals
ERC20_DECIMALS_ABI = [{"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"}]

# Constant: default investment token decimals (USDC-like tokens commonly 6; project requires 18)
INVESTMENT_TOKEN_DECIMALS_DEFAULT = 18

logger = logging.getLogger(__name__)

class BlockchainService:
    """Service for blockchain operations and smart contract deployment"""
    
    def __init__(self):
        self.w3 = None
        self.account = None
        self.usdc_address = None
        self._setup_connection()
    
    def _setup_connection(self):
        """Setup blockchain connection"""
        try:
            logger.info(f"🔗 Setting up blockchain connection for network: {settings.network}")
            
            # Get network-specific configuration
            rpc_url = settings.rpc_url
            private_key = settings.private_key
            self.usdc_address = settings.usdc_address
            
            logger.info(f"📍 Using {settings.network} network: {rpc_url}")
            
            # Initialize Web3
            self.w3 = Web3(Web3.HTTPProvider(rpc_url))
            
            # Add PoA middleware for networks like Polygon
            if settings.network.upper() in ['POLYGON', 'SEPOLIA']:
                self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            
            # Check connection
            if not self.w3.is_connected():
                raise Exception(f"Failed to connect to {settings.network} network")
            
            logger.info(f"✅ Connected to {settings.network} network")
            logger.info(f"🔗 Chain ID: {self.w3.eth.chain_id}")
            logger.info(f"📊 Latest block: {self.w3.eth.block_number}")
            
            # Setup account
            if not private_key:
                raise Exception("Private key not configured")
            
            self.account = Account.from_key(private_key)
            logger.info(f"👤 Account address: {self.account.address}")
            
            # Check account balance
            balance_wei = self.w3.eth.get_balance(self.account.address)
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            logger.info(f"💰 Account balance: {balance_eth} ETH")
            
        except Exception as e:
            logger.error(f"❌ Failed to setup blockchain connection: {str(e)}")
            raise
    
    async def get_gas_price_with_safety_margin(self) -> int:
        """Get current gas price with a safety margin"""
        try:
            current_gas_price = self.w3.eth.gas_price
            # Add a 20% safety margin
            safe_gas_price = int(current_gas_price * 1.20)
            logger.debug(f"Current gas price: {current_gas_price}, Safe gas price: {safe_gas_price}")
            return safe_gas_price
        except Exception as e:
            logger.error(f"Error getting gas price: {e}. Using default gas price.")
            return self.w3.to_wei(30, 'gwei')  # Default to 30 gwei
    
    async def get_gas_limit_with_safety_margin(self, tx: dict) -> int:
        """Get gas limit with safety margin"""
        try:
            estimated_gas = self.w3.eth.estimate_gas(tx)
            # Add 50% safety margin for deployments
            safe_gas_limit = int(estimated_gas * 1.50)
            logger.debug(f"Estimated gas: {estimated_gas}, Safe gas limit: {safe_gas_limit}")
            return safe_gas_limit
        except Exception as e:
            logger.error(f"Error estimating gas: {e}. Using default gas limit.")
            return 5000000  # Default gas limit
    
    def _get_gas_price(self) -> int:
        """Get gas price for transactions"""
        try:
            return self.w3.eth.gas_price
        except Exception as e:
            logger.error(f"Error getting gas price: {e}")
            return self.w3.to_wei(30, 'gwei')
    
    def _get_nonce(self) -> int:
        """Get nonce for transactions"""
        try:
            return self.w3.eth.get_transaction_count(self.account.address)
        except Exception as e:
            logger.error(f"Error getting nonce: {e}")
            return 0
    
    def _estimate_gas(self, tx: dict) -> int:
        """Estimate gas for transaction"""
        try:
            return self.w3.eth.estimate_gas(tx)
        except Exception as e:
            logger.error(f"Error estimating gas: {e}")
            return 5000000
    
    async def _send_transaction(self, tx: dict, description: str) -> str:
        """Send transaction with retry logic"""
        max_retries = 3
        base_delay = 2
        
        for attempt in range(max_retries):
            try:
                logger.info(f"📤 Sending transaction (attempt {attempt + 1}/{max_retries}): {description}")
                
                # Sign transaction
                signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
                logger.info(f"✍️  Transaction signed")
                
                # Send transaction
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                logger.info(f"📤 Transaction sent: {tx_hash.hex()}")
                
                # Wait for confirmation
                logger.info(f"⏳ Waiting for transaction confirmation...")
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
                
                if receipt.status == 1:
                    logger.info(f"✅ Transaction confirmed: {tx_hash.hex()}")
                    logger.info(f"📊 Gas used: {receipt.gasUsed}")
                    logger.info(f"📊 Block number: {receipt.blockNumber}")
                    return tx_hash.hex()
                else:
                    raise Exception(f"Transaction failed with status: {receipt.status}")
                    
            except Exception as e:
                logger.error(f"❌ Transaction attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"⏳ Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    raise Exception(f"Transaction failed after {max_retries} attempts: {str(e)}")
    
    async def deploy_fundraising_token(
        self, 
        name: str, 
        symbol: str, 
        decimals: int = 18, 
        initial_supply: int = 1000000,
        business_admin: str = None
    ) -> Tuple[str, str]:
        """Deploy FundraisingToken contract"""
        try:
            logger.info(f"🚀 Deploying FundraisingToken contract...")
            logger.info(f"📋 Contract details: name={name}, symbol={symbol}, decimals={decimals}, initial_supply={initial_supply}")
            logger.info(f"📋 Business admin: {business_admin}")
            
            # Check if contract is compiled
            if not FUNDRAISINGTOKEN_BYTECODE or FUNDRAISINGTOKEN_BYTECODE == "0x":
                raise Exception("FundraisingToken contract not compiled")
            
            # Use provided business admin or default to deployer
            if business_admin is None:
                business_admin = self.account.address
            # Ensure business admin address is checksummed for on-chain usage
            business_admin = Web3.to_checksum_address(business_admin)
            
            # Get gas price and nonce
            gas_price = await self.get_gas_price_with_safety_margin()
            nonce = self._get_nonce()
            
            # Create contract instance
            contract = self.w3.eth.contract(
                abi=FUNDRAISINGTOKEN_ABI,
                bytecode=FUNDRAISINGTOKEN_BYTECODE
            )
            
            # Build constructor transaction with business admin parameter
            constructor_tx = contract.constructor(
                name, symbol, decimals, business_admin, initial_supply
            ).build_transaction({
                "from": self.account.address,
                "gasPrice": gas_price,
                "nonce": nonce
            })
            
            # Estimate gas
            gas_estimate = await self.get_gas_limit_with_safety_margin(constructor_tx)
            constructor_tx["gas"] = gas_estimate
            
            # Send transaction
            tx_hash = await self._send_transaction(constructor_tx, "FundraisingToken deployment")
            
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
            raise
    
    async def deploy_ieo_contract(
        self, 
        token_address: str, 
        admin_address: str, 
        business_admin_address: str,
        delay_days: int,
        min_investment: int,
        max_investment: int
    ) -> Tuple[str, str]:
        """Deploy IEO contract"""
        try:
            logger.info(f"🚀 Deploying IEO contract...")
            logger.info(f"📋 Contract details: token={token_address}, admin={admin_address}, business_admin={business_admin_address}")
            logger.info(f"📋 IEO settings: delay_days={delay_days}, min_investment={min_investment}, max_investment={max_investment}")
            
            # Check if contract is compiled
            if not IEO_BYTECODE or IEO_BYTECODE == "0x":
                raise Exception("IEO contract not compiled")
            
            # Ensure addresses are checksummed for on-chain usage
            token_address = Web3.to_checksum_address(token_address)
            admin_address = Web3.to_checksum_address(admin_address)
            business_admin_address = Web3.to_checksum_address(business_admin_address)

            # Values are pre-scaled (project service applies 10^decimals). Pass through unchanged.
            min_scaled = int(min_investment)
            max_scaled = int(max_investment)
            logger.info(f"⚙️ Using pre-scaled min/max: min={min_scaled}, max={max_scaled}")
            
            # Get gas price and nonce
            gas_price = await self.get_gas_price_with_safety_margin()
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
                min_scaled,
                max_scaled
            ).build_transaction({
                'from': self.account.address,
                'gasPrice': gas_price,
                'nonce': nonce
            })
            
            # Estimate gas
            gas_estimate = await self.get_gas_limit_with_safety_margin(constructor_tx)
            constructor_tx['gas'] = gas_estimate
            
            # Send transaction
            tx_hash = await self._send_transaction(constructor_tx, "IEO contract deployment")
            
            # Get contract address from receipt
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            contract_address = receipt.contractAddress
            
            logger.info(f"✅ IEO contract deployed successfully!")
            logger.info(f"📍 Contract address: {contract_address}")
            logger.info(f"🔗 Transaction: {tx_hash}")
            
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

            # Ensure addresses are checksummed for on-chain usage
            token_address = Web3.to_checksum_address(token_address)
            ieo_contract_address = Web3.to_checksum_address(ieo_contract_address)
            
            if not REWARDTRACKING_BYTECODE or REWARDTRACKING_BYTECODE == "0x":
                raise Exception("RewardTracking contract not compiled")
            
            # Get gas price and nonce
            gas_price = await self.get_gas_price_with_safety_margin()
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
            gas_estimate = await self.get_gas_limit_with_safety_margin(constructor_tx)
            constructor_tx['gas'] = gas_estimate
            
            # Send transaction
            tx_hash = await self._send_transaction(constructor_tx, "RewardTracking contract deployment")
            
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
    
    async def deploy_project_contracts(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy all contracts for a project"""
        try:
            logger.info(f"🚀 Starting project contract deployment...")
            logger.info(f"📋 Project: {project_data['name']} ({project_data['symbol']})")
            
            # Step 1: Deploy FundraisingToken
            logger.info(f"📝 Step 1/3: Deploying FundraisingToken...")
            token_address, token_tx = await self.deploy_fundraising_token(
                name=project_data["name"],
                symbol=project_data["symbol"],
                decimals=18,
                initial_supply=project_data["initial_supply"],
                business_admin=project_data["business_admin_wallet"]
            )
            
            # Add delay between deployments
            await asyncio.sleep(2)
            
            # Step 2: Deploy IEO contract
            logger.info(f"📝 Step 2/3: Deploying IEO contract...")
            ieo_address, ieo_tx = await self.deploy_ieo_contract(
                token_address=token_address,
                admin_address=self.account.address,  # Deployer as admin
                business_admin_address=project_data['business_admin_wallet'],
                delay_days=project_data['delay_days'],
                min_investment=project_data['min_investment'],
                max_investment=project_data['max_investment']
            )
            
            # Add delay between deployments
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
            
            # Note: Tokens are already minted to business admin in constructor
            logger.info(f"✅ Tokens already minted to business admin in constructor")
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
            # For now, we'll just log that configuration is complete
            logger.info(f"✅ Contracts configured successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to configure contracts: {str(e)}")
            raise


    async def set_oracle_address(self, ieo_contract_address: str, oracle_address: str) -> str:
        """Set oracle address for IEO contract"""
        try:
            logger.info(f"🔮 Setting oracle address {oracle_address} for IEO contract {ieo_contract_address}")
            
            # Create IEO contract instance
            ieo_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(ieo_contract_address),
                abi=IEO_ABI
            )
            
            # Get gas price and nonce
            gas_price = await self.get_gas_price_with_safety_margin()
            nonce = self._get_nonce()
            
            # Build transaction - function name in IEO.sol is setPriceOracle(address)
            tx = ieo_contract.functions.setPriceOracle(Web3.to_checksum_address(oracle_address)).build_transaction({
                'from': self.account.address,
                'gasPrice': gas_price,
                'nonce': nonce
            })
            
            # Estimate gas
            gas_estimate = await self.get_gas_limit_with_safety_margin(tx)
            tx['gas'] = gas_estimate
            
            # Send transaction
            tx_hash = await self._send_transaction(tx, f"Set oracle address {oracle_address}")
            
            logger.info(f"✅ Oracle address set: {tx_hash}")
            return tx_hash
            
        except Exception as e:
            logger.error(f"❌ Failed to set oracle address: {str(e)}")
            raise


    async def get_ieo_status(self, ieo_contract_address: str) -> Dict[str, Any]:
        """Get IEO contract status"""
        try:
            logger.info(f"📊 Getting IEO status for contract: {ieo_contract_address}")
            
            # Create IEO contract instance
            ieo_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(ieo_contract_address),
                abi=IEO_ABI
            )
            
            # Get IEO status information
            try:
                is_active = ieo_contract.functions.isActive().call()
            except:
                is_active = False
            
            try:
                total_raised = ieo_contract.functions.totalRaised().call()
            except:
                total_raised = 0
            
            try:
                min_investment = ieo_contract.functions.minInvestment().call()
            except:
                min_investment = 0
            
            try:
                max_investment = ieo_contract.functions.maxInvestment().call()
            except:
                max_investment = 0
            
            try:
                delay_days = ieo_contract.functions.delayDays().call()
            except:
                delay_days = 0
            
            status_info = {
                'is_active': is_active,
                'total_raised': total_raised,
                'min_investment': min_investment,
                'max_investment': max_investment,
                'delay_days': delay_days,
                'contract_address': ieo_contract_address
            }
            
            logger.info(f"✅ IEO status retrieved: {status_info}")
            return status_info
            
        except Exception as e:
            logger.error(f"❌ Failed to get IEO status: {str(e)}")
            raise


    async def get_token_price(self, oracle_contract_address: str, token_address: str) -> Dict[str, Any]:
        """Get token price from oracle"""
        try:
            logger.info(f"💰 Getting token price from oracle {oracle_contract_address} for token {token_address}")
            
            # Create oracle contract instance
            oracle_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(oracle_contract_address),
                abi=MOCKPRICEORACLE_ABI
            )
            
            # Call the oracle contract using checksum token address
            price, decimals, timestamp = oracle_contract.functions.getPrice(
                Web3.to_checksum_address(token_address)
            ).call()
            
            price_data = {
                'price': price,
                'decimals': decimals,
                'timestamp': timestamp
            }
            
            logger.info(f"✅ Token price retrieved: {price_data}")
            return price_data
            
        except Exception as e:
            logger.error(f"❌ Failed to get token price: {str(e)}")
            raise

    async def is_whitelisted(self, token_contract_address: str, address: str) -> bool:
        """Check if an address is whitelisted on a FundraisingToken contract."""
        try:
            token_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(token_contract_address),
                abi=FUNDRAISINGTOKEN_ABI
            )
            return token_contract.functions.isWhitelisted(
                Web3.to_checksum_address(address)
            ).call()
        except Exception as e:
            logger.error(f"❌ Failed to check whitelist status for {address} on {token_contract_address}: {e}")
            return False

    # New methods: update business admin on Token and IEO contracts
    async def set_token_business_admin(self, token_contract_address: str, new_business_admin: str) -> str:
        """Set business admin on FundraisingToken contract"""
        try:
            logger.info(f"👤 Setting token business admin to {new_business_admin} on {token_contract_address}")
            token_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(token_contract_address),
                abi=FUNDRAISINGTOKEN_ABI
            )
            gas_price = await self.get_gas_price_with_safety_margin()
            nonce = self._get_nonce()
            tx = token_contract.functions.setBusinessAdmin(
                Web3.to_checksum_address(new_business_admin)
            ).build_transaction({
                'from': self.account.address,
                'gasPrice': gas_price,
                'nonce': nonce
            })
            gas_estimate = await self.get_gas_limit_with_safety_margin(tx)
            tx['gas'] = gas_estimate
            tx_hash = await self._send_transaction(tx, f"Set token business admin {new_business_admin}")
            logger.info(f"✅ Token business admin updated: {tx_hash}")
            return tx_hash
        except Exception as e:
            logger.error(f"❌ Failed to set token business admin: {str(e)}")
            raise

    async def set_ieo_business_admin(self, ieo_contract_address: str, new_business_admin: str) -> str:
        """Set business admin on IEO contract"""
        try:
            logger.info(f"👤 Setting IEO business admin to {new_business_admin} on {ieo_contract_address}")
            ieo_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(ieo_contract_address),
                abi=IEO_ABI
            )
            gas_price = await self.get_gas_price_with_safety_margin()
            nonce = self._get_nonce()
            tx = ieo_contract.functions.setBusinessAdmin(
                Web3.to_checksum_address(new_business_admin)
            ).build_transaction({
                'from': self.account.address,
                'gasPrice': gas_price,
                'nonce': nonce
            })
            gas_estimate = await self.get_gas_limit_with_safety_margin(tx)
            tx['gas'] = gas_estimate
            tx_hash = await self._send_transaction(tx, f"Set IEO business admin {new_business_admin}")
            logger.info(f"✅ IEO business admin updated: {tx_hash}")
            return tx_hash
        except Exception as e:
            logger.error(f"❌ Failed to set IEO business admin: {str(e)}")
            raise

# Create service instance

blockchain_service = BlockchainService()
