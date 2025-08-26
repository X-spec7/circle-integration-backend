# FastAPI Backend with Authentication & User Types

A scalable FastAPI backend with user registration, login functionality, and user type support (SME and Investor) using PostgreSQL database.

## Features

- **User Authentication**: Registration and login with JWT tokens
- **User Types**: Support for SME (Small and Medium Enterprises) and Investor users
- **Scalable Architecture**: Clean, modular structure for easy feature additions
- **PostgreSQL Integration**: Robust database with SQLAlchemy ORM
- **Password Security**: Bcrypt hashing for secure password storage
- **API Documentation**: Interactive Swagger UI and ReDoc
- **Database Migrations**: Alembic for schema management
- **Environment Management**: Secure configuration with dotenv
- **CORS Support**: Cross-origin resource sharing middleware
- **Comprehensive Validation**: Pydantic schemas for request/response validation

## Architecture

The application follows a clean, scalable architecture:

```
app/
├── core/                 # Core configuration and utilities
│   ├── config.py        # Application settings
│   ├── database.py      # Database connection
│   └── security.py      # Authentication utilities
├── models/              # SQLAlchemy database models
│   └── user.py          # User model with types
├── schemas/             # Pydantic validation schemas
│   ├── user.py          # User request/response schemas
│   └── auth.py          # Authentication schemas
├── services/            # Business logic layer
│   └── user_service.py  # User operations
├── api/                 # API routes
│   ├── deps.py          # Dependency injection
│   └── v1/              # API version 1
│       ├── api.py       # Main API router
│       └── endpoints/   # Individual endpoint modules
│           ├── auth.py  # Authentication endpoints
│           └── users.py # User management endpoints
├── utils/               # Utility functions
│   └── response.py      # Standardized responses
└── main.py              # FastAPI application
```

## User Types

The system supports two user types:

- **SME (Small and Medium Enterprises)**: For business entities seeking investment
- **Investor**: For entities looking to invest in businesses

## Prerequisites

- Python 3.8+
- PostgreSQL database running in Docker
- pip (Python package manager)

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

## 🚀 Development

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

## Production Deployment

For production deployment:

1. **Environment Configuration**:
   - Set `DEBUG=false`
   - Use strong `SECRET_KEY`
   - Configure proper `CORS_ORIGINS`
   - Use production database URL

2. **Security Considerations**:
   - Use HTTPS
   - Configure proper CORS origins
   - Set up rate limiting
   - Use environment variables for secrets
   - Enable database connection pooling

3. **Performance Optimization**:
   - Use production ASGI server (Gunicorn)
   - Configure database connection pooling
   - Set up proper logging
   - Enable caching where appropriate

## 🔄 Adding New Features

The modular structure makes it easy to add new features:

1. **Add new models** in `app/models/`
2. **Create schemas** in `app/schemas/`
3. **Implement business logic** in `app/services/`
4. **Add API endpoints** in `app/api/v1/endpoints/`
5. **Update dependencies** in `app/api/deps.py`
