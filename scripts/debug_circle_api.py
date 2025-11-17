"""
Debug script to see raw Circle API responses
"""
import asyncio
import sys
import os
import json

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.circle_client import CircleClient
from app.core.config import settings

async def debug_circle_api():
    """Debug Circle API responses"""
    
    print("Debugging Circle API Responses")
    print("=" * 50)
    
    if not settings.circle_api_key:
        print("❌ CIRCLE_API_KEY not configured")
        return
    
    print(f"✅ Using Circle API Key: {settings.circle_api_key[:10]}...")
    print(f"✅ Using Circle Base URL: {settings.circle_base_url}")
    print()
    
    circle_client = CircleClient()
    
    try:
        # Test business account balances
        print("1. Testing /businessAccount/balances:")
        print("-" * 40)
        response = await circle_client.get_business_account_balance()
        print("Raw response:")
        print(json.dumps(response, indent=2))
        print()
        
        # Test wallets (should fail with 403)
        print("2. Testing /wallets:")
        print("-" * 40)
        try:
            response = await circle_client.get_all_wallets()
            print("Raw response:")
            print(json.dumps(response, indent=2))
        except Exception as e:
            print(f"Error: {str(e)}")
        print()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        
    finally:
        await circle_client.close()

if __name__ == "__main__":
    asyncio.run(debug_circle_api()) 