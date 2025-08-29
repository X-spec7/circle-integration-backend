#!/usr/bin/env python3
"""
Test script for Circle payment flow
Tests the complete flow: Card Payment → EUR → EURC → USDC → Escrow
"""
import asyncio
import sys
import os
from decimal import Decimal

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.circle_payment_flow import CirclePaymentFlow
from app.core.config import settings

async def test_circle_payment_flow():
    """Test the complete Circle payment flow"""
    
    print("Testing Circle Payment Flow")
    print("=" * 50)
    
    # Check configuration
    print("1. Checking configuration...")
    if not settings.circle_api_key:
        print("   ❌ CIRCLE_API_KEY not configured")
        return
    else:
        print("   ✅ CIRCLE_API_KEY configured")
    
    if not settings.circle_mint_wallet_id:
        print("   ⚠️  CIRCLE_MINT_WALLET_ID not configured (will be needed for payouts)")
    else:
        print("   ✅ CIRCLE_MINT_WALLET_ID configured")
    
    print()
    
    # Initialize payment flow service
    payment_flow = CirclePaymentFlow()
    
    try:
        # Test 1: Get business account information
        print("2. Testing business account info...")
        try:
            account_info = await payment_flow.get_business_account_info()
            if "error" not in account_info:
                print("   ✅ Business account info retrieved")
                print(f"   Banks: {len(account_info.get('banks', []))}")
                print(f"   Balances: {len(account_info.get('balances', []))}")
            else:
                print(f"   ❌ Error getting business account info: {account_info['error']}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        print()
        
        # Test 2: Test card payment intent creation
        print("3. Testing card payment intent creation...")
        try:
            # This is a test - in real scenario, you'd get these from the database
            test_amount = Decimal("10.00")  # 10 EUR
            test_project_name = "Test Project"
            test_escrow_address = "0x1234567890123456789012345678901234567890"  # Test address
            test_project_id = "test-project-123"
            
            result = await payment_flow.process_card_payment_to_escrow(
                amount=test_amount,
                project_name=test_project_name,
                escrow_address=test_escrow_address,
                project_id=test_project_id
            )
            
            if result["status"] == "success":
                print("   ✅ Payment flow completed successfully")
                print(f"   Payment ID: {result.get('payment_id')}")
                print(f"   Conversion ID: {result.get('conversion_id')}")
                print(f"   Recipient ID: {result.get('recipient_id')}")
                print(f"   Payout ID: {result.get('payout_id')}")
                print(f"   Flow: {result.get('flow')}")
                
                # Test 3: Get status of components
                print()
                print("4. Testing status retrieval...")
                try:
                    status = await payment_flow.get_payment_flow_status(
                        payment_id=result.get('payment_id'),
                        payout_id=result.get('payout_id')
                    )
                    print("   ✅ Status retrieved successfully")
                    print(f"   Status data: {status}")
                except Exception as e:
                    print(f"   ❌ Error getting status: {str(e)}")
                    
            else:
                print(f"   ❌ Payment flow failed: {result.get('error')}")
                
        except Exception as e:
            print(f"   ❌ Error in payment flow: {str(e)}")
        
        print()
        
        # Test 4: Test individual components
        print("5. Testing individual components...")
        
        # Test currency conversion
        try:
            conversion_result = await payment_flow._convert_eurc_to_usdc(Decimal("5.00"))
            print("   ✅ Currency conversion test successful")
        except Exception as e:
            print(f"   ❌ Currency conversion test failed: {str(e)}")
        
        # Test address book addition
        try:
            recipient_result = await payment_flow._add_escrow_to_address_book(
                "0x1234567890123456789012345678901234567890",
                "Test Project"
            )
            print("   ✅ Address book addition test successful")
        except Exception as e:
            print(f"   ❌ Address book addition test failed: {str(e)}")
        
    except Exception as e:
        print(f"Error in test: {str(e)}")
    
    finally:
        await payment_flow.close()
    
    print()
    print("Test completed!")

if __name__ == "__main__":
    asyncio.run(test_circle_payment_flow()) 