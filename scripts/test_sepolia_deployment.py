"""
Test script for deploying contracts on Sepolia testnet
"""
import asyncio
import sys
import os
from decimal import Decimal
from datetime import datetime, timedelta

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.blockchain_service import blockchain_service
from app.core.config import settings

async def test_sepolia_deployment():
    """Test the deployment of all 3 contracts on Sepolia"""
    print("Testing Sepolia Testnet Deployment")
    print("=" * 50)
    print(f"Network: {settings.network}")
    print(f"RPC URL: {settings.rpc_url}")
    print(f"USDC Address: {settings.usdc_address}")
    print(f"Account Address: {blockchain_service.account.address}")
    print()
    
    try:
        # Test project data
        project_data = {
            'name': 'Test Solar Project',
            'symbol': 'TSP',
            'initial_supply': 1000000,  # 1M tokens
            'admin_address': blockchain_service.account.address,
            'business_admin_address': blockchain_service.account.address,
            'delay_days': 7,
            'min_investment': 100,  # $100 minimum in USDC (6 decimals)
            'max_investment': 1000000  # $1M maximum in USDC (6 decimals)
        }
        
        print(f"Deploying contracts for: {project_data['name']}")
        print(f"Symbol: {project_data['symbol']}")
        print(f"Initial Supply: {project_data['initial_supply']:,}")
        print(f"Delay Days: {project_data['delay_days']}")
        print(f"Min Investment: ${project_data['min_investment']}")
        print(f"Max Investment: ${project_data['max_investment']:,}")
        print()
        
        # Deploy all contracts
        result = await blockchain_service.deploy_project_contracts(
            name=project_data['name'],
            symbol=project_data['symbol'],
            initial_supply=project_data['initial_supply'],
            admin_address=project_data['admin_address'],
            business_admin_address=project_data['business_admin_address'],
            delay_days=project_data['delay_days'],
            min_investment=project_data['min_investment'],
            max_investment=project_data['max_investment']
        )
        
        print("✅ Deployment Successful!")
        print()
        print("Contract Addresses:")
        print(f"  Token Contract: {result['token_contract']['address']}")
        print(f"  IEO Contract: {result['ieo_contract']['address']}")
        print(f"  Reward Tracking: {result['reward_tracking_contract']['address']}")
        print()
        print("Transaction Hashes:")
        print(f"  Token Deployment: {result['token_contract']['deployment']['transaction_hash']}")
        print(f"  IEO Deployment: {result['ieo_contract']['deployment']['transaction_hash']}")
        print(f"  Reward Tracking Deployment: {result['reward_tracking_contract']['deployment']['transaction_hash']}")
        print()
        print("Gas Used:")
        print(f"  Token: {result['token_contract']['deployment']['gas_used']:,}")
        print(f"  IEO: {result['ieo_contract']['deployment']['gas_used']:,}")
        print(f"  Reward Tracking: {result['reward_tracking_contract']['deployment']['gas_used']:,}")
        
        total_gas = (
            result['token_contract']['deployment']['gas_used'] +
            result['ieo_contract']['deployment']['gas_used'] +
            result['reward_tracking_contract']['deployment']['gas_used']
        )
        print(f"  Total: {total_gas:,}")
        
        print()
        print("🔗 View on Etherscan:")
        base_url = "https://sepolia.etherscan.io" if settings.network.upper() == "SEPOLIA" else "https://polygonscan.com"
        print(f"  Token: {base_url}/address/{result['token_contract']['address']}")
        print(f"  IEO: {base_url}/address/{result['ieo_contract']['address']}")
        print(f"  Reward Tracking: {base_url}/address/{result['reward_tracking_contract']['address']}")
        
    except Exception as e:
        print(f"❌ Deployment Failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_sepolia_deployment())
