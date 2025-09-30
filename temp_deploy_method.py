    async def deploy_fundraising_token(
        self, 
        name: str, 
        symbol: str, 
        decimals: int = 18, 
        initial_supply: int = 1000000,
        business_admin: str = None
    ) -> Tuple[str, str]:
        """Deploy FundraisingToken contract"""
        try:
            logger.info(f"🚀 Deploying FundraisingToken contract...")
            logger.info(f"📋 Contract details: name={name}, symbol={symbol}, decimals={decimals}, initial_supply={initial_supply}")
            logger.info(f"📋 Business admin: {business_admin}")
            
            # Check if contract is compiled
            if not FUNDRAISINGTOKEN_BYTECODE or FUNDRAISINGTOKEN_BYTECODE == "0x":
                raise Exception("FundraisingToken contract not compiled")
            
            # Use provided business admin or default to deployer
            if business_admin is None:
                business_admin = self.account.address
            
            # Get gas price and nonce
            gas_price = await self.get_gas_price_with_safety_margin()
            nonce = self._get_nonce()
            
            # Create contract instance
            contract = self.w3.eth.contract(
                abi=FUNDRAISINGTOKEN_ABI,
                bytecode=FUNDRAISINGTOKEN_BYTECODE
            )
            
            # Build constructor transaction with business admin parameter
            constructor_tx = contract.constructor(
                name, symbol, decimals, business_admin, initial_supply
            ).build_transaction({
                'from': self.account.address,
                'gasPrice': gas_price,
                'nonce': nonce
            })
            
            # Estimate gas
            gas_estimate = await self.get_gas_limit_with_safety_margin(constructor_tx)
            constructor_tx['gas'] = gas_estimate
            
            # Send transaction
            tx_hash = await self._send_transaction(constructor_tx, "FundraisingToken deployment")
            
            # Get contract address from receipt
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            contract_address = receipt.contractAddress
            
            logger.info(f"✅ FundraisingToken deployed successfully!")
            logger.info(f"📍 Contract address: {contract_address}")
            logger.info(f"🔗 Transaction: {tx_hash}")
            
            return contract_address, tx_hash
            
        except Exception as e:
            logger.error(f"❌ Failed to deploy FundraisingToken: {str(e)}")
            raise
