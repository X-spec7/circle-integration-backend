#!/usr/bin/env python3
"""
Test Contract Deployment Script
Deploys test ERC20 token and escrow contracts on Polygon testnet (Mumbai)
"""

import asyncio
import logging
from decimal import Decimal
from web3 import Web3
from eth_account import Account
from datetime import datetime, timedelta

# Import compiled contract constants
from compiled_contracts.contract_constants import (
    SIMPLEERC20_ABI, SIMPLEERC20_BYTECODE,
    SIMPLEESCROW_ABI, SIMPLEESCROW_BYTECODE
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestDeployment:
    def __init__(self):
        # Polygon Mumbai testnet
        self.w3 = Web3(Web3.HTTPProvider("https://rpc-mumbai.maticvigil.com"))
        
        # Test private key (generated for testing)
        self.private_key = "0x3debcba82ab24b7f8eb2f2342c108f6cd65bc91234104801ce99cc29d11cccb7"
        self.account = Account.from_key(self.private_key)
        self.w3.eth.default_account = self.account.address
        
        # USDC test address on Mumbai
        self.usdc_address = "0xe6b8a5CF854791412c1f6EFC7CAf629f5Df1c747"  # Mumbai USDC
        
        logger.info(f"Test deployment initialized with address: {self.account.address}")
        logger.info(f"Network: {self.w3.eth.chain_id}")
        logger.info(f"Balance: {self.w3.eth.get_balance(self.account.address)} wei")
    
    async def deploy_erc20_token(self, name: str, symbol: str, total_supply: int, price_per_token: Decimal, owner_address: str):
        """Deploy ERC20 token contract"""
        try:
            logger.info(f"Deploying ERC20 token: {name} ({symbol})")
            
            # Convert price to wei (18 decimals)
            price_wei = int(price_per_token * Decimal('1e18'))
            
            # Create contract instance
            contract = self.w3.eth.contract(
                abi=SIMPLEERC20_ABI,
                bytecode=SIMPLEERC20_BYTECODE
            )
            
            # Prepare constructor parameters
            constructor_params = [
                name,
                symbol,
                total_supply,
                price_wei,
                owner_address
            ]
            
            # Build transaction
            transaction = contract.constructor(*constructor_params).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 3000000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            logger.info(f"Token deployment transaction sent: {tx_hash.hex()}")
            
            # Wait for transaction receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if tx_receipt.status == 1:
                contract_address = tx_receipt.contractAddress
                logger.info(f" ERC20 token deployed successfully!")
                logger.info(f"Contract Address: {contract_address}")
                logger.info(f"Transaction Hash: {tx_hash.hex()}")
                logger.info(f"Gas Used: {tx_receipt.gasUsed}")
                return contract_address, tx_hash.hex()
            else:
                raise Exception("Token deployment failed")
                
        except Exception as e:
            logger.error(f" Error deploying ERC20 token: {str(e)}")
            raise
    
    async def deploy_escrow_contract(self, project_token_address: str, project_owner_address: str, target_amount: Decimal, token_price: Decimal, end_date: int):
        """Deploy escrow contract"""
        try:
            logger.info(f"Deploying escrow contract for token: {project_token_address}")
            
            # Convert amounts to wei (6 decimals for USDC)
            target_amount_wei = int(target_amount * Decimal('1e6'))
            token_price_wei = int(token_price * Decimal('1e6'))
            
            # Create contract instance
            contract = self.w3.eth.contract(
                abi=SIMPLEESCROW_ABI,
                bytecode=SIMPLEESCROW_BYTECODE
            )
            
            # Prepare constructor parameters
            constructor_params = [
                project_token_address,
                self.usdc_address,
                project_owner_address,
                target_amount_wei,
                token_price_wei,
                end_date
            ]
            
            # Build transaction
            transaction = contract.constructor(*constructor_params).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 4000000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            logger.info(f"Escrow deployment transaction sent: {tx_hash.hex()}")
            
            # Wait for transaction receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if tx_receipt.status == 1:
                contract_address = tx_receipt.contractAddress
                logger.info(f" Escrow contract deployed successfully!")
                logger.info(f"Contract Address: {contract_address}")
                logger.info(f"Transaction Hash: {tx_hash.hex()}")
                logger.info(f"Gas Used: {tx_receipt.gasUsed}")
                return contract_address, tx_hash.hex()
            else:
                raise Exception("Escrow deployment failed")
                
        except Exception as e:
            logger.error(f" Error deploying escrow contract: {str(e)}")
            raise
    
    async def test_deployment(self):
        """Test deployment of both contracts"""
        try:
            logger.info(" Starting test deployment on Polygon Mumbai testnet...")
            
            # Test parameters
            token_name = "Test Project Token"
            token_symbol = "TPT"
            total_supply = 1000000 * 10**18  # 1 million tokens with 18 decimals
            price_per_token = Decimal('1.00')  # $1 per token
            project_owner = self.account.address
            
            # Deploy ERC20 token
            token_address, token_tx = await self.deploy_erc20_token(
                name=token_name,
                symbol=token_symbol,
                total_supply=total_supply,
                price_per_token=price_per_token,
                owner_address=project_owner
            )
            
            # Deploy escrow contract
            target_amount = Decimal('10000.00')  # $10,000 target
            end_date = int((datetime.now() + timedelta(days=30)).timestamp())  # 30 days from now
            
            escrow_address, escrow_tx = await self.deploy_escrow_contract(
                project_token_address=token_address,
                project_owner_address=project_owner,
                target_amount=target_amount,
                token_price=price_per_token,
                end_date=end_date
            )
            
            # Print summary
            logger.info("\n" + "="*60)
            logger.info(" DEPLOYMENT SUMMARY")
            logger.info("="*60)
            logger.info(f"Network: Polygon Mumbai Testnet")
            logger.info(f"Deployer: {self.account.address}")
            logger.info(f"")
            logger.info(f" ERC20 Token Contract:")
            logger.info(f"   Address: {token_address}")
            logger.info(f"   Name: {token_name}")
            logger.info(f"   Symbol: {token_symbol}")
            logger.info(f"   Total Supply: {total_supply / 10**18:,} tokens")
            logger.info(f"   Price: ${price_per_token}")
            logger.info(f"   Owner: {project_owner}")
            logger.info(f"   Transaction: {token_tx}")
            logger.info(f"")
            logger.info(f" Escrow Contract:")
            logger.info(f"   Address: {escrow_address}")
            logger.info(f"   Project Token: {token_address}")
            logger.info(f"   USDC Token: {self.usdc_address}")
            logger.info(f"   Target Amount: ${target_amount}")
            logger.info(f"   Token Price: ${price_per_token}")
            logger.info(f"   End Date: {datetime.fromtimestamp(end_date)}")
            logger.info(f"   Transaction: {escrow_tx}")
            logger.info(f"")
            logger.info(f" Mumbai Polygonscan Links:")
            logger.info(f"   Token: https://mumbai.polygonscan.com/address/{token_address}")
            logger.info(f"   Escrow: https://mumbai.polygonscan.com/address/{escrow_address}")
            logger.info(f"   Token TX: https://mumbai.polygonscan.com/tx/{token_tx}")
            logger.info(f"   Escrow TX: https://mumbai.polygonscan.com/tx/{escrow_tx}")
            logger.info("="*60)
            
            return {
                'token_address': token_address,
                'escrow_address': escrow_address,
                'token_tx': token_tx,
                'escrow_tx': escrow_tx
            }
            
        except Exception as e:
            logger.error(f" Test deployment failed: {str(e)}")
            raise

async def main():
    """Main test function"""
    try:
        deployer = TestDeployment()
        result = await deployer.test_deployment()
        
        # Return the addresses for the user
        print(f"\n CONTRACT ADDRESSES FOR TESTING:")
        print(f"Token Contract: {result['token_address']}")
        print(f"Escrow Contract: {result['escrow_address']}")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 