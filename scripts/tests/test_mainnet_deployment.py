#!/usr/bin/env python3
"""
Mainnet Contract Deployment Test
Deploys ERC20 token and escrow contracts on Polygon mainnet
"""

import asyncio
import logging
from decimal import Decimal
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the blockchain service
from app.services.blockchain_service import blockchain_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MainnetDeploymentTest:
    def __init__(self):
        self.blockchain_service = blockchain_service
        logger.info(f"Mainnet deployment test initialized")
        logger.info(f"Network: Polygon Mainnet")
        logger.info(f"Deployer: {self.blockchain_service.account.address}")
    
    async def test_erc20_deployment(self):
        """Test ERC20 token deployment on mainnet"""
        try:
            logger.info("\n" + "="*60)
            logger.info(" DEPLOYING ERC20 TOKEN ON POLYGON MAINNET")
            logger.info("="*60)
            
            # Test parameters
            token_name = "Test Project Token"
            token_symbol = "TPT"
            total_supply = 1000000 * 10**18  # 1 million tokens
            price_per_token = Decimal('1.00')
            owner_address = self.blockchain_service.account.address
            
            logger.info(" Deployment Parameters:")
            logger.info(f"   Token Name: {token_name}")
            logger.info(f"   Symbol: {token_symbol}")
            logger.info(f"   Total Supply: {total_supply / 10**18:,} tokens")
            logger.info(f"   Price per Token: ${price_per_token}")
            logger.info(f"   Owner: {owner_address}")
            
            # Deploy the token
            logger.info("\n Deploying ERC20 token contract...")
            token_address, deployment_info = await self.blockchain_service.deploy_erc20_token(
                name=token_name,
                symbol=token_symbol,
                total_supply=total_supply,
                price_per_token=price_per_token,
                owner_address=owner_address
            )
            
            logger.info(" ERC20 token deployed successfully!")
            logger.info(f"   Contract Address: {token_address}")
            logger.info(f"   Transaction Hash: {deployment_info['transaction_hash']}")
            logger.info(f"   Block Number: {deployment_info['block_number']}")
            logger.info(f"   Gas Used: {deployment_info['gas_used']}")
            
            return token_address, deployment_info
            
        except Exception as e:
            logger.error(f" ERC20 deployment failed: {str(e)}")
            raise
    
    async def test_escrow_deployment(self, token_address: str):
        """Test escrow contract deployment on mainnet"""
        try:
            logger.info("\n" + "="*60)
            logger.info(" DEPLOYING ESCROW CONTRACT ON POLYGON MAINNET")
            logger.info("="*60)
            
            # Test parameters
            project_owner = self.blockchain_service.account.address
            target_amount = Decimal('10000.00')  # $10,000 target
            token_price = Decimal('1.00')
            end_date = int((datetime.now() + timedelta(days=30)).timestamp())
            
            logger.info(" Deployment Parameters:")
            logger.info(f"   Project Token: {token_address}")
            logger.info(f"   USDC Token: {self.blockchain_service.usdc_address}")
            logger.info(f"   Project Owner: {project_owner}")
            logger.info(f"   Target Amount: ${target_amount}")
            logger.info(f"   Token Price: ${token_price}")
            logger.info(f"   End Date: {datetime.fromtimestamp(end_date)}")
            
            # Deploy the escrow
            logger.info("\n Deploying escrow contract...")
            escrow_address, deployment_info = await self.blockchain_service.deploy_escrow_contract(
                project_token_address=token_address,
                project_owner_address=project_owner,
                target_amount=target_amount,
                token_price=token_price,
                end_date=end_date
            )
            
            logger.info(" Escrow contract deployed successfully!")
            logger.info(f"   Contract Address: {escrow_address}")
            logger.info(f"   Transaction Hash: {deployment_info['transaction_hash']}")
            logger.info(f"   Block Number: {deployment_info['block_number']}")
            logger.info(f"   Gas Used: {deployment_info['gas_used']}")
            
            return escrow_address, deployment_info
            
        except Exception as e:
            logger.error(f" Escrow deployment failed: {str(e)}")
            raise
    
    async def run_mainnet_deployment_test(self):
        """Run the complete mainnet deployment test"""
        try:
            logger.info(" POLYGON MAINNET DEPLOYMENT TEST")
            logger.info("This test deploys real contracts on Polygon mainnet")
            
            # Check deployer balance
            balance = self.blockchain_service.w3.eth.get_balance(self.blockchain_service.account.address)
            balance_matic = self.blockchain_service.w3.from_wei(balance, 'ether')
            logger.info(f" Deployer Balance: {balance_matic} MATIC")
            
            if balance_matic < 0.1:
                logger.warning(" Low balance! Need at least 0.1 MATIC for deployment")
            
            # Deploy ERC20 token
            token_address, token_deployment = await self.test_erc20_deployment()
            
            # Deploy escrow contract
            escrow_address, escrow_deployment = await self.test_escrow_deployment(token_address)
            
            # Print final summary
            logger.info("\n" + "="*60)
            logger.info(" MAINNET DEPLOYMENT SUMMARY")
            logger.info("="*60)
            logger.info(f"Network: Polygon Mainnet")
            logger.info(f"Deployer: {self.blockchain_service.account.address}")
            logger.info(f"")
            logger.info(f" ERC20 Token Contract:")
            logger.info(f"   Address: {token_address}")
            logger.info(f"   Transaction: {token_deployment['transaction_hash']}")
            logger.info(f"   Block: {token_deployment['block_number']}")
            logger.info(f"")
            logger.info(f" Escrow Contract:")
            logger.info(f"   Address: {escrow_address}")
            logger.info(f"   Transaction: {escrow_deployment['transaction_hash']}")
            logger.info(f"   Block: {escrow_deployment['block_number']}")
            logger.info(f"")
            logger.info(f" Polygonscan Links:")
            logger.info(f"   Token: https://polygonscan.com/address/{token_address}")
            logger.info(f"   Escrow: https://polygonscan.com/address/{escrow_address}")
            logger.info(f"   Token TX: https://polygonscan.com/tx/{token_deployment['transaction_hash']}")
            logger.info(f"   Escrow TX: https://polygonscan.com/tx/{escrow_deployment['transaction_hash']}")
            logger.info("="*60)
            
            return {
                'token_address': token_address,
                'escrow_address': escrow_address,
                'token_deployment': token_deployment,
                'escrow_deployment': escrow_deployment
            }
            
        except Exception as e:
            logger.error(f" Mainnet deployment test failed: {str(e)}")
            raise

async def main():
    """Main test function"""
    try:
        # Check if environment variables are set
        polygon_rpc = os.getenv('POLYGON_RPC_URL')
        polygon_key = os.getenv('POLYGON_PRIVATE_KEY')
        
        if not polygon_rpc:
            logger.error(" POLYGON_RPC_URL not found in .env file")
            return
        
        if not polygon_key:
            logger.error(" POLYGON_PRIVATE_KEY not found in .env file")
            return
        
        logger.info(f" Environment variables loaded")
        logger.info(f"   RPC URL: {polygon_rpc[:50]}...")
        logger.info(f"   Private Key: {polygon_key[:10]}...")
        
        # Run the deployment test
        test = MainnetDeploymentTest()
        result = await test.run_mainnet_deployment_test()
        
        # Print the contract addresses for the user
        print(f"\n CONTRACT ADDRESSES ON POLYGON MAINNET:")
        print(f"Token Contract: {result['token_address']}")
        print(f"Escrow Contract: {result['escrow_address']}")
        print(f"\n Transaction Hashes:")
        print(f"Token Deployment: {result['token_deployment']['transaction_hash']}")
        print(f"Escrow Deployment: {result['escrow_deployment']['transaction_hash']}")
        print(f"\n View on Polygonscan:")
        print(f"Token: https://polygonscan.com/address/{result['token_address']}")
        print(f"Escrow: https://polygonscan.com/address/{result['escrow_address']}")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 