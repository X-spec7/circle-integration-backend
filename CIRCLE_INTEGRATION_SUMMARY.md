## Payment Flow

### Fiat Payment Flow (EUR via SEPA)

1. **Investor initiates payment** → `POST /api/v1/payments/initiate`
2. **Backend creates Circle payment intent** → Circle API `/payments`
3. **Investor receives bank details** → IBAN, BIC, reference number
4. **Investor transfers EUR** → Bank transfer to Circle IBAN
5. **Circle on-ramps to EURC** → Automatic conversion
6. **Circle webhook notification** → `POST /api/v1/payments/webhooks/circle`
7. **Backend transfers EURC to escrow** → Circle API `/transfers`
8. **Investment confirmed** → Database updated, tokens allocated

### Crypto Payment Flow

1. **Investor initiates crypto payment** → `POST /api/v1/payments/crypto`
2. **Backend provides escrow address** → Project-specific smart contract
3. **Investor sends USDC** → Direct transfer to escrow
4. **Investment confirmed** → Database updated, tokens allocated

## Implementation Details

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
```

### API Endpoints

#### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/users/me` - Get current user

#### Projects
- `POST /api/v1/projects/` - Create project (SME only)
- `GET /api/v1/projects/` - List active projects
- `GET /api/v1/projects/{id}` - Get project details
- `PUT /api/v1/projects/{id}` - Update project (owner only)

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
ESCROW_WALLET_ADDRESS=0x123...

# Security
SECRET_KEY=your_jwt_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

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

# Test project creation
curl -X POST "http://localhost:8001/api/v1/projects/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Project","symbol":"TEST","description":"Test description","category":"Technology","target_amount":10000.00,"price_per_token":1.00,"total_supply":1000000,"end_date":"2025-12-31T23:59:59","risk_level":"Medium"}'
```

## Monitoring & Logging

- **Structured Logging** - Python logging with JSON format
- **Error Tracking** - Comprehensive error handling
- **Payment Status Tracking** - Real-time payment monitoring
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
    # Transfer EURC to escrow if needed
```
