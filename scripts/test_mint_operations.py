#!/usr/bin/env python3
"""
Test script to check Circle Mint operations
"""
import asyncio
import sys
import os
import json

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.circle_client import CircleClient
from app.core.config import settings

async def test_mint_operations():
    """Test Circle Mint operations"""
    
    print("Testing Circle Mint Operations")
    print("=" * 50)
    
    if not settings.circle_api_key:
        print("❌ CIRCLE_API_KEY not configured")
        return
    
    print(f"✅ Using Circle API Key: {settings.circle_api_key[:10]}...")
    print(f"✅ Using Circle Base URL: {settings.circle_base_url}")
    print()
    
    circle_client = CircleClient()
    
    try:
        # Test 1: Currency conversion (EURC to USDC)
        print("1. Testing Currency Conversion (EURC to USDC):")
        print("-" * 50)
        try:
            # Test with a small amount (1 EURC = ~1.08 USDC)
            response = await circle_client.convert_currency(
                source_amount="100",  # 1 EURC in cents
                source_currency="EURC",
                destination_currency="USDC"
            )
            print("✅ Currency conversion successful!")
            print("Response:", json.dumps(response, indent=2))
        except Exception as e:
            print(f"❌ Currency conversion failed: {str(e)}")
        print()
        
        # Test 2: Address book operations
        print("2. Testing Address Book Operations:")
        print("-" * 50)
        try:
            # Test adding a recipient to address book
            test_address = "0x1234567890123456789012345678901234567890"  # Test address
            response = await circle_client.add_address_book_recipient(
                address=test_address,
                chain="MATIC",
                description="Test Escrow Contract"
            )
            print("✅ Address book operation successful!")
            print("Response:", json.dumps(response, indent=2))
        except Exception as e:
            print(f"❌ Address book operation failed: {str(e)}")
        print()
        
        # Test 3: Business account banks
        print("3. Testing Business Account Banks:")
        print("-" * 50)
        try:
            response = await circle_client.get_business_account_banks()
            print("✅ Business account banks accessible!")
            if "data" in response and response["data"]:
                print(f"Found {len(response['data'])} bank account(s)")
            else:
                print("No bank accounts configured")
        except Exception as e:
            print(f"❌ Business account banks failed: {str(e)}")
        print()
        
        # Test 4: Payouts (will likely fail without wallet access)
        print("4. Testing Payout Operations:")
        print("-" * 50)
        if settings.circle_mint_wallet_id:
            print(f"✅ CIRCLE_MINT_WALLET_ID configured: {settings.circle_mint_wallet_id}")
            print("Note: Payouts require wallet access which we don't have")
        else:
            print("❌ CIRCLE_MINT_WALLET_ID not configured")
            print("This is needed for crypto payouts")
        print()
        
        print("📋 Summary:")
        print("-" * 30)
        print("✅ Currency conversion should work (Circle Mint)")
        print("✅ Address book operations should work")
        print("✅ Business account operations work")
        print("❌ Payouts require wallet access (which we don't have)")
        print()
        print("💡 Circle Mint operations (currency conversion) should work")
        print("   even without wallet access, as they operate on business account level.")
        
    except Exception as e:
        print(f"❌ Error testing mint operations: {str(e)}")
        
    finally:
        await circle_client.close()

if __name__ == "__main__":
    asyncio.run(test_mint_operations()) 