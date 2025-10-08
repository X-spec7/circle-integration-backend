## Fiat Payments (Circle) - Backend Configuration

### Overview
This backend integrates with Circle to accept fiat (SEPA, card), converts to USDC in Circle Mint, and then pays out crypto on-chain. A webhook from Circle marks payments successful and triggers conversion + payout.

### Environment Variables
- `CIRCLE_API_KEY` (required): Circle API key.
- `CIRCLE_BASE_URL` (optional): defaults to `https://api.circle.com/v1` (use sandbox base if testing).
- `CIRCLE_MINT_WALLET_ID` (required): Circle Mint wallet ID to fund crypto payouts.

Blockchain config (used elsewhere):
- `NETWORK`, `SEPOLIA_RPC_URL`, `SEPOLIA_WS_RPC_URL`, `SEPOLIA_WALLET_PRIVATE_KEY`, etc.

### Key Endpoints
- Webhooks (handled by backend):
  - `HEAD /api/v1/payments/webhooks/circle` (endpoint validation)
  - `POST /api/v1/payments/webhooks/circle` (payment events)

### Webhook Verification
- The backend verifies Circle’s ECDSA signature using headers:
  - `X-Circle-Signature`
  - `X-Circle-Key-Id`
- Public key is fetched from Circle (`/v2/notifications/publicKey/{keyId}`) and used to verify the request body.

### Payment Flow (High-Level)
1) Client initiates a payment (fiat/card). Backend creates an `Investment` and a Circle payment intent.
2) Circle notifies the backend via webhook when the payment is successful (`payment.successful`).
3) Backend marks the `Payment`/`Investment` completed, then:
   - Converts EUR→EURC→USDC in Circle (via `convert_currency`).
   - Adds destination on-chain address to the Circle Address Book (if needed).
   - Creates a crypto payout from Circle Mint to the destination address.

### Current Destination Address
- Implemented destination: `project.escrow_contract_address` (if present).
- Recommended per current architecture: send directly to the IEO contract (`project.ieo_contract_address`) so funds land in the sale contract.

### Recording the On-Chain Investment (Admin)
- Smart contract now supports: `adminRecordInvestment(address investor, uint256 usdcAmount)`.
- Intended use: after Circle payout lands in the IEO contract, the backend (admin key) records the user’s investment specifying the whitelisted `investor` wallet and `usdcAmount` in on-chain units (match IEO’s `USDC_DECIMALS`).
- This function calculates tokens using the oracle and appends to `userInvestments[investor]`, emitting `InvestmentMade`.

### Amount Units and Decimals
- Circle API amounts are expressed as fiat currency amounts (the code uses integer cents for requests).
- On-chain `usdcAmount` must be in token units used by the IEO contract. Ensure the backend passes amounts scaled to IEO’s `USDC_DECIMALS` when calling `adminRecordInvestment`.

### What’s Configured vs. What’s Pending
Configured:
- Payment intents for SEPA and card
- Webhook verification (ECDSA) and payment status handling
- EURC→USDC conversion and crypto payout via Circle Mint

Pending/Recommended Updates:
- Use `project.ieo_contract_address` as payout destination instead of `escrow_contract_address`.
- After payout success, call `IEO.adminRecordInvestment(investor, usdcAmount)` from the backend with an admin key.
- Ensure the `investor` wallet is whitelisted in the token contract beforehand to enable later claims/transfers.
- Confirm `Project` model has the destination address field you intend to use. If using IEO, no extra field is needed; if escrow is still required, make sure `escrow_contract_address` exists in the model and DB schema.

### Files of Interest
- Backend payment flow: `app/services/payment_service.py`
- Circle client: `app/services/circle_client.py`
- Webhook endpoints: `app/api/v1/endpoints/payments.py`
- IEO contract (admin record function): `app/contracts/IEO.sol` / `interfaces/IIEO.sol`


