# FastAPI Backend with Authentication & User Types

A scalable FastAPI backend with user registration, login functionality, and user type support (SME and Investor) using PostgreSQL database.

## User Types

The system supports two user types:

- **SME (Small and Medium Enterprises)**: For business entities seeking investment
- **Investor**: For entities looking to invest in businesses

## Prerequisites

- Python 3.8+
- PostgreSQL database running in Docker
- pip (Python package manager)
- Redis (for WebSocket fanout across instances)

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd circle-integration-backend
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   make install
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the root directory with the following content:
   ```env
   DB_URL=postgresql://your_username:your_password@localhost:5432/your_database
   SECRET_KEY=your-secret-key-here-change-this-in-production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   DEBUG=false
   # Redis for WS fanout
   REDIS_URL=redis://localhost:6379/0
   # ComplyCube (KYC)
   COMPLYCUBE_BASE_URL=https://api.complycube.com/v1
   # IMPORTANT: include 'Bearer ' prefix unless code handles it for you.
   COMPLYCUBE_API_KEY=Bearer sk_test_xxx
   COMPLYCUBE_WEBHOOK_SECRET=your-complycube-webhook-secret
   # Circle (see FIAT_PAYMENTS.md for details)
   CIRCLE_API_KEY=
   CIRCLE_BASE_URL=https://api.circle.com/v1
   CIRCLE_MINT_WALLET_ID=
   # Blockchain (optional, for realtime event listener)
   NETWORK=SEPOLIA
   SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
   SEPOLIA_WS_RPC_URL=wss://sepolia.infura.io/ws/v3/YOUR_PROJECT_ID
   ```
   
   Replace the values with your actual database credentials and a secure secret key.
   ```env
   DB_URL=postgresql://your_username:your_password@localhost:5432/your_database
   SECRET_KEY=your-secret-key-here-change-this-in-production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   DEBUG=false
   ```

5. **Run the application**
   ```bash
   make dev
   ```

### Optional: Start Redis locally
```bash
docker run -p 6379:6379 --name redis -d redis:7
```

## Available Commands

The project includes a Makefile with convenient commands:

```bash
make help          # Show all available commands
make install       # Install dependencies
make dev           # Run in development mode (port 8888)
make run           # Run in production mode (port 8888)
make test          # Run tests
make migrate       # Create new migration
make migrate-up    # Apply migrations
make migrate-down  # Rollback last migration
make clean         # Clean up cache files
```

## Database Migrations

The application uses Alembic for database migrations:

1. **Create initial migration**:
   ```bash
   make migrate message="Initial migration"
   ```

2. **Apply migrations**:
   ```bash
   make migrate-up
   ```

3. **Rollback migration**:
   ```bash
   make migrate-down
   ```
## API Documentation

Once the server is running, access:

- **Swagger UI**: http://localhost:8888/docs
- **ReDoc**: http://localhost:8888/redoc

### API Guides
- KYC (ComplyCube): see `KYC_API.md`
- Fiat Payments (Circle): see `FIAT_PAYMENTS.md`
- WebSockets overview and client examples: see `WEBSOCKETS.md`

##  Development

### Available Make Commands
```bash
make help          # Show all available commands
make install       # Install dependencies
make dev           # Run in development mode with auto-reload
make run           # Run in production mode
make test          # Run tests
make migrate       # Create new migration (use: make migrate message="Description")
make migrate-up    # Apply migrations
make migrate-down  # Rollback last migration
make clean         # Clean up cache files
```

### Running in Development Mode
```bash
make dev
```

Notes:
- WebSockets endpoints:
  - `/api/v1/ws/notifications?token=<JWT>`
  - `/api/v1/ws/tickets/{ticket_id}?token=<JWT>`
- WS authentication uses a `token` query param for the HTTP→WS upgrade. Use WSS in production and short-lived JWTs.
- Redis is required for cross-instance fanout; the app will still work locally without Redis if you are on a single instance, but fanout is disabled.

### Running in Production Mode
```bash
make run
```

### Database Operations
```bash
# Create migration
make migrate message="Description"

# Apply migrations
make migrate-up

# Rollback migration
make migrate-down
```
