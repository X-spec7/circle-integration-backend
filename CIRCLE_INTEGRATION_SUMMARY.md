## Payment Flow

### Fiat Payment Flow (EUR via SEPA)

1. **Investor initiates payment** → `POST /api/v1/payments/initiate`
2. **Backend creates Circle payment intent** → Circle API `/payments`
3. **Investor receives bank details** → IBAN, BIC, reference number
4. **Investor transfers EUR** → Bank transfer to Circle IBAN
5. **Circle on-ramps to EURC** → Automatic conversion
6. **Circle webhook notification** → `POST /api/v1/payments/webhooks/circle`
7. **Backend transfers EURC to escrow** → Blockchain transaction to project escrow
8. **Investment confirmed** → Database updated, tokens allocated

### Crypto Payment Flow

1. **Investor initiates crypto payment** → `POST /api/v1/payments/crypto`
2. **Backend provides escrow address** → Project-specific smart contract
3. **Investor sends USDC** → Direct transfer to escrow
4. **Investment confirmed** → Database updated, tokens allocated

## Blockchain Integration

### Project Creation with Smart Contracts

1. **SME creates project** → `POST /api/v1/projects/`
2. **Backend deploys ERC20 token** → Polygon mainnet deployment
3. **Backend deploys escrow contract** → Project-specific escrow
4. **Project activated** → Ready for investments

### Smart Contract Architecture

#### ERC20 Token Contract (`app/contracts/erc20_template.py`)
- **Features**: Standard ERC20 with project-specific functionality
- **Owner**: Project creator (SME)
- **Functions**: Transfer, burn, pause/unpause, price updates
- **Deployment**: Automatic on project creation

#### Escrow Contract (`app/contracts/escrow_template.py`)
- **Features**: Fund management and token distribution
- **Owner**: Platform (for emergency controls)
- **Functions**: Investment, token claiming, fund release, refunds
- **Deployment**: Automatic on project creation

## Implementation Details

### Blockchain Service (`app/services/blockchain_service.py`)

```python
class BlockchainService:
    async def deploy_erc20_token(self, name, symbol, total_supply, price_per_token, owner_address)
    async def deploy_escrow_contract(self, project_token_address, project_owner_address, target_amount, token_price, end_date)
    async def transfer_eurc_to_escrow(self, escrow_address, amount)
    async def get_contract_balance(self, contract_address, token_address)
    async def get_transaction_status(self, tx_hash)
```

### Project Service (`app/services/project_service.py`)

```python
class ProjectService:
    async def create_project(self, db, user, project_data) -> ProjectDeploymentResponse
    async def get_project(self, db, project_id) -> Optional[Project]
    async def update_project(self, db, project_id, user, update_data) -> Project
    async def get_escrow_address(self, db, project_id) -> Optional[str]
```

### Circle API Client (`app/services/circle_client.py`)

```python
class CircleClient:
    async def create_payment_intent(self, amount: str, currency: str = "EUR")
    async def get_payment_status(self, payment_id: str)
    async def transfer_to_escrow(self, amount: str, currency: str, escrow_address: str)
    async def get_transfer_status(self, transfer_id: str)
```

### Payment Service (`app/services/payment_service.py`)

```python
class PaymentService:
    async def create_investment(self, db: Session, user: User, investment_data: InvestmentCreate)
    async def initiate_payment(self, db: Session, user: User, payment_data: PaymentInitiateRequest)
    async def process_circle_webhook(self, db: Session, webhook_data: Dict[str, Any])
    # Enhanced with blockchain integration for EURC transfers
```

### API Endpoints

#### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/users/me` - Get current user

#### Projects
- `POST /api/v1/projects/` - Create project with blockchain deployment (SME only)
- `GET /api/v1/projects/` - List active projects
- `GET /api/v1/projects/{id}` - Get project details with contract addresses
- `PUT /api/v1/projects/{id}` - Update project (owner only)
- `GET /api/v1/projects/{id}/escrow-address` - Get project escrow address

#### Payments
- `POST /api/v1/payments/initiate` - Initiate payment
- `POST /api/v1/payments/crypto` - Initiate crypto payment
- `GET /api/v1/payments/{id}/status` - Get payment status
- `POST /api/v1/payments/confirm` - Confirm payment
- `GET /api/v1/payments/investments` - Get user investments
- `POST /api/v1/payments/webhooks/circle` - Circle webhook handler

## 🔧 Configuration

### Environment Variables

```env
# Database
DB_URL=postgresql://username:password@localhost:5432/database_name

# Circle API
CIRCLE_API_KEY=your_circle_api_key
CIRCLE_BASE_URL=https://api.circle.com/v1
CIRCLE_WEBHOOK_SECRET=your_webhook_secret

# Blockchain
NETWORK=POLYGON
POLYGON_RPC_URL=https://polygon-rpc.com
POLYGON_PRIVATE_KEY=your_private_key_for_deployment
ESCROW_WALLET_ADDRESS=0x123...

# Security
SECRET_KEY=your_jwt_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Smart Contract Deployment

#### Prerequisites
1. **Private Key**: Wallet with sufficient POL for gas fees
2. **Polygon RPC**: Reliable RPC endpoint for mainnet
3. **Contract Compilation**: Smart contracts need to be compiled to bytecode

#### Deployment Process
1. **Token Deployment**: ERC20 token with project parameters
2. **Escrow Deployment**: Escrow contract linked to token
3. **Address Storage**: Contract addresses stored in database
4. **Status Update**: Project status set to ACTIVE

### Circle API Setup

1. **Create Circle Account** - Sign up at circle.com
2. **Get API Keys** - Generate sandbox and production keys
3. **Configure Webhooks** - Set webhook URL to your endpoint
4. **Set up Treasury Account** - Configure EURC settlement

### API Testing

```bash
# Test root endpoint
curl -X GET "http://localhost:8001/"

# Test user registration
curl -X POST "http://localhost:8001/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"testpass123","name":"Test User","user_type":"investor"}'

# Test project creation with blockchain deployment
curl -X POST "http://localhost:8001/api/v1/projects/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Project","symbol":"TEST","description":"Test description","category":"Technology","target_amount":10000.00,"price_per_token":1.00,"total_supply":1000000,"end_date":"2025-12-31T23:59:59","risk_level":"Medium"}'

# Test escrow address retrieval
curl -X GET "http://localhost:8001/api/v1/projects/PROJECT_ID/escrow-address"
```

## Monitoring & Logging

- **Structured Logging** - Python logging with JSON format
- **Error Tracking** - Comprehensive error handling
- **Payment Status Tracking** - Real-time payment monitoring
- **Blockchain Transaction Monitoring** - Contract deployment and transfer tracking
- **Database Monitoring** - Connection pooling and health checks

## Webhook Processing

### Circle Webhook Events

- `payment.successful` - Fiat payment completed
- `payment.failed` - Fiat payment failed
- `transfer.completed` - EURC transfer to escrow completed

### Webhook Handler

```python
@router.post("/webhooks/circle")
async def circle_webhook(request: Request, db: Session = Depends(get_db)):
    # Verify webhook signature
    # Process payment status update
    # Update investment records
    # Transfer EURC to escrow via blockchain
```

## Frontend Integration

### API Integration Requirements

1. **Project Creation** - Include blockchain deployment response handling
2. **Blockchain Information Display** - Show contract addresses and transaction hashes
3. **Enhanced Investment Flow** - Support for both fiat and crypto payments
4. **Transaction Monitoring** - Real-time status updates
5. **Escrow Address Display** - Show project-specific escrow addresses

### Key API Changes

- Project creation now returns contract addresses and deployment transaction hashes
- Payment status includes blockchain transaction information
- New endpoint to retrieve project escrow addresses

See `FRONTEND_INTEGRATION_GUIDE.md` for detailed API integration instructions.

## Security Considerations

### Smart Contract Security
- **Access Control** - Proper owner and role management
- **Reentrancy Protection** - Use ReentrancyGuard
- **Input Validation** - Validate all constructor parameters
- **Emergency Functions** - Pause/unpause capabilities

### API Security
- **Authentication** - JWT token validation
- **Authorization** - Role-based access control
- **Input Sanitization** - Validate all user inputs
- **Rate Limiting** - Prevent abuse

### Private Key Management
- **Environment Variables** - Store private keys securely
- **Access Control** - Limit access to deployment keys
- **Monitoring** - Track all transactions
- **Backup** - Secure backup of critical keys

## Deployment Checklist

### Backend Deployment
- [ ] Set up environment variables
- [ ] Install blockchain dependencies (web3, eth-account)
- [ ] Compile smart contracts
- [ ] Test on Polygon testnet
- [ ] Deploy to production
- [ ] Configure Circle webhooks
- [ ] Set up monitoring

### Frontend Deployment
- [ ] Update environment variables
- [ ] Test project creation flow
- [ ] Test payment integration
- [ ] Verify blockchain links
- [ ] Deploy to production

### Post-Deployment
- [ ] Monitor contract deployments
- [ ] Track payment processing
- [ ] Monitor gas usage
- [ ] Set up alerts for failures
- [ ] Document any issues
