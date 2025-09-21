#!/usr/bin/env python3
"""
Test script to check Circle API access and available endpoints
"""
import requests
import json
import sys
import os

def test_circle_api(api_key):
    """Test various Circle API endpoints"""
    
    base_urls = [
        "https://api.circle.com/v1",
        "https://api-sandbox.circle.com/v1"
    ]
    
    endpoints = [
        "/wallets",
        "/businessAccount/balances", 
        "/businessAccount/banks/wire",
        "/payments",
        "/conversions"
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print("Testing Circle API Access")
    print("=" * 50)
    print(f"API Key: {api_key[:20]}...")
    print()
    
    for base_url in base_urls:
        print(f"Testing {base_url}:")
        print("-" * 30)
        
        for endpoint in endpoints:
            url = f"{base_url}{endpoint}"
            try:
                response = requests.get(url, headers=headers, timeout=10)
                print(f"  {endpoint}: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    if "data" in data:
                        print(f"    ✅ Success - Found {len(data['data'])} items")
                    else:
                        print(f"    ✅ Success - Response: {json.dumps(data, indent=4)[:200]}...")
                elif response.status_code == 401:
                    print(f"    ❌ Unauthorized")
                elif response.status_code == 403:
                    print(f"    ❌ Forbidden - Permission denied")
                elif response.status_code == 404:
                    print(f"    ❌ Not Found - Endpoint doesn't exist")
                else:
                    print(f"    ❌ Error {response.status_code}: {response.text[:100]}...")
                    
            except Exception as e:
                print(f"  {endpoint}: ❌ Exception - {str(e)}")
        
        print()

if __name__ == "__main__":
    # Get API key from environment or command line
    api_key = None
    
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        # Try to get from .env file
        try:
            with open('.env', 'r') as f:
                for line in f:
                    if line.startswith('CIRCLE_API_KEY='):
                        api_key = line.split('=', 1)[1].strip()
                        break
        except:
            pass
    
    if not api_key:
        print("Usage: python3 test_circle_api.py <api_key>")
        print("Or set CIRCLE_API_KEY in .env file")
        sys.exit(1)
    
    test_circle_api(api_key) 