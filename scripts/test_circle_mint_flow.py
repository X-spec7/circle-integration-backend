"""
Test script for Circle Mint payment flow (no wallet access required)
"""
import asyncio
import sys
import os
import json
from decimal import Decimal

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.circle_payment_flow import CirclePaymentFlow
from app.core.config import settings

async def test_circle_mint_flow():
    """Test the Circle Mint payment flow"""
    
    print("Testing Circle Mint Payment Flow")
    print("=" * 50)
    
    if not settings.circle_api_key:
        print("❌ CIRCLE_API_KEY not configured")
        return
    
    print(f"✅ Using Circle API Key: {settings.circle_api_key[:10]}...")
    print(f"✅ Using Circle Base URL: {settings.circle_base_url}")
    print()
    
    # Test parameters
    test_amount = Decimal("10.00")  # 10 EUR
    test_project_name = "Test Project"
    test_escrow_address = "0x1234567890123456789012345678901234567890"  # Test address
    test_project_id = "test_project_123"
    
    print(f"🧪 Test Parameters:")
    print(f"   Amount: {test_amount} EUR")
    print(f"   Project: {test_project_name}")
    print(f"   Escrow Address: {test_escrow_address}")
    print(f"   Project ID: {test_project_id}")
    print()
    
    payment_flow = CirclePaymentFlow()
    
    try:
        print("🚀 Testing Complete Payment Flow:")
        print("-" * 40)
        
        # Test the complete flow
        result = await payment_flow.process_card_payment_to_escrow(
            amount=test_amount,
            project_name=test_project_name,
            escrow_address=test_escrow_address,
            project_id=test_project_id
        )
        
        print("📋 Flow Result:")
        print(json.dumps(result, indent=2))
        print()
        
        if result["status"] == "success":
            print("✅ Payment flow completed successfully!")
            print()
            print("📊 Flow Components:")
            print(f"   Payment ID: {result.get('payment_id', 'N/A')}")
            print(f"   Conversion ID: {result.get('conversion_id', 'N/A')}")
            print(f"   Transfer ID: {result.get('transfer_id', 'N/A')}")
            print()
            
            # Test status checking
            print("🔍 Testing Status Check:")
            print("-" * 30)
            
            status_result = await payment_flow.get_payment_flow_status(
                payment_id=result.get('payment_id'),
                conversion_id=result.get('conversion_id'),
                transfer_id=result.get('transfer_id')
            )
            
            print("Status Result:")
            print(json.dumps(status_result, indent=2))
            
        else:
            print("❌ Payment flow failed:")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error testing payment flow: {str(e)}")
        print()
        print("💡 This might be expected if:")
        print("   - Currency conversion is not available")
        print("   - Transfer permissions are limited")
        print("   - Test escrow address is invalid")
        
    finally:
        await payment_flow.close()

async def test_individual_components():
    """Test individual components of the payment flow"""
    
    print("\n🔧 Testing Individual Components:")
    print("=" * 50)
    
    payment_flow = CirclePaymentFlow()
    
    try:
        # Test 1: Card payment intent
        print("1. Testing Card Payment Intent:")
        print("-" * 30)
        try:
            result = await payment_flow._create_card_payment_intent(
                amount=Decimal("5.00"),
                description="Test Payment"
            )
            print("✅ Card payment intent created successfully")
            print(f"   Payment ID: {result['data']['id']}")
        except Exception as e:
            print(f"❌ Card payment intent failed: {str(e)}")
        print()
        
        # Test 2: Currency conversion
        print("2. Testing Currency Conversion:")
        print("-" * 30)
        try:
            result = await payment_flow._convert_eurc_to_usdc(Decimal("5.00"))
            print("✅ Currency conversion successful")
            print(f"   Conversion ID: {result['data']['id']}")
        except Exception as e:
            print(f"❌ Currency conversion failed: {str(e)}")
        print()
        
        # Test 3: Mint transfer
        print("3. Testing Mint Transfer:")
        print("-" * 30)
        try:
            result = await payment_flow._create_usdc_transfer_to_escrow(
                amount=Decimal("5.00"),
                escrow_address="0x1234567890123456789012345678901234567890",
                project_id="test_123"
            )
            print("✅ Mint transfer successful")
            print(f"   Transfer ID: {result['data']['id']}")
        except Exception as e:
            print(f"❌ Mint transfer failed: {str(e)}")
        print()
        
    except Exception as e:
        print(f"❌ Error testing components: {str(e)}")
        
    finally:
        await payment_flow.close()

if __name__ == "__main__":
    print("Circle Mint Payment Flow Test")
    print("=" * 50)
    print("This test verifies that the payment flow works with Circle Mint")
    print("without requiring wallet access or address book operations.")
    print()
    
    asyncio.run(test_circle_mint_flow())
    asyncio.run(test_individual_components()) 