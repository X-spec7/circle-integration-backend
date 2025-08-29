#!/usr/bin/env python3
"""
Test script for Circle webhook endpoint
"""
import httpx
import json
import asyncio
from typing import Dict, Any

async def test_webhook_endpoint(base_url: str = "http://localhost:8000") -> None:
    """
    Test the Circle webhook endpoint
    """
    webhook_url = f"{base_url}/api/v1/webhooks/circle"
    
    print("Testing Circle webhook endpoint...")
    print(f"URL: {webhook_url}")
    print("-" * 50)
    
    async with httpx.AsyncClient() as client:
        # Test HEAD request
        print("1. Testing HEAD request...")
        try:
            head_response = await client.head(webhook_url)
            print(f"   Status: {head_response.status_code}")
            if head_response.status_code == 200:
                print("   ✅ HEAD request successful")
            else:
                print("   ❌ HEAD request failed")
        except Exception as e:
            print(f"   ❌ HEAD request error: {e}")
        
        print()
        
        # Test POST request with sample webhook data
        print("2. Testing POST request...")
        sample_webhook = {
            "subscriptionId": "test-subscription-id",
            "notificationId": "test-notification-id",
            "notificationType": "webhooks.test",
            "notification": {
                "hello": "world"
            },
            "timestamp": "2024-01-26T18:22:19.779834211Z",
            "version": 2
        }
        
        try:
            post_response = await client.post(
                webhook_url,
                json=sample_webhook,
                headers={"Content-Type": "application/json"}
            )
            print(f"   Status: {post_response.status_code}")
            print(f"   Response: {post_response.text}")
            
            if post_response.status_code in [200, 201, 202]:
                print("   ✅ POST request successful")
            else:
                print("   ❌ POST request failed")
        except Exception as e:
            print(f"   ❌ POST request error: {e}")
        
        print()
        
        # Test POST request with Circle signature headers (will fail without valid signature)
        print("3. Testing POST request with Circle signature headers...")
        try:
            post_response_with_sig = await client.post(
                webhook_url,
                json=sample_webhook,
                headers={
                    "Content-Type": "application/json",
                    "X-Circle-Signature": "invalid-signature",
                    "X-Circle-Key-Id": "invalid-key-id"
                }
            )
            print(f"   Status: {post_response_with_sig.status_code}")
            print(f"   Response: {post_response_with_sig.text}")
            
            if post_response_with_sig.status_code == 401:
                print("   ✅ Signature verification working (rejected invalid signature)")
            else:
                print("   ⚠️  Unexpected response for invalid signature")
        except Exception as e:
            print(f"   ❌ POST request with signature error: {e}")

if __name__ == "__main__":
    asyncio.run(test_webhook_endpoint()) 