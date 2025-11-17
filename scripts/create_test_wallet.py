"""
Create Test Wallet Script
Generates a test wallet for Polygon Mumbai testnet deployment
"""

from eth_account import Account
import secrets

def create_test_wallet():
    """Create a new test wallet"""
    # Generate a random private key
    private_key = "0x" + secrets.token_hex(32)
    account = Account.from_key(private_key)
    
    print("Test Wallet Generated")
    print("=" * 50)
    print(f"Private Key: {private_key}")
    print(f"Address: {account.address}")
    print("=" * 50)
    print("\n To get test MATIC:")
    print("1. Go to: https://faucet.polygon.technology/")
    print("2. Select 'Mumbai' network")
    print("3. Enter your address: " + account.address)
    print("4. Request test MATIC")
    print("\n  WARNING: This is for testing only!")
    print("Never use this private key for real funds!")
    
    return private_key, account.address

if __name__ == "__main__":
    create_test_wallet() 