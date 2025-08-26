.PHONY: help install run dev test migrate migrate-up migrate-down clean

# Virtual environment path
VENV = venv/bin/activate

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install dependencies"
	@echo "  run          - Run the FastAPI application"
	@echo "  dev          - Run in development mode with auto-reload"
	@echo "  test         - Run tests"
	@echo "  migrate      - Create a new migration (use: make migrate message=\"Description\")"
	@echo "  migrate-up   - Apply migrations"
	@echo "  migrate-down - Rollback last migration"
	@echo "  clean        - Clean up cache and temporary files"

# Install dependencies
install:
	@echo "Installing dependencies..."
	@if [ ! -d "venv" ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv venv; \
	fi
	. $(VENV) && python3 -m pip install -r requirements.txt

# Run the application
run:
	@echo "Starting FastAPI application on port 8888..."
	. $(VENV) && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8888

# Run in development mode with auto-reload
dev:
	@echo "Starting FastAPI application in development mode on port 8888..."
	. $(VENV) && python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8888

# Run tests
test:
	@echo "Running tests..."
	. $(VENV) && python3 -m pytest

# Create a new migration
migrate:
	@echo "Creating new migration..."
	@if [ -z "$(message)" ]; then \
		echo "Error: Please provide a message. Usage: make migrate message=\"Description\""; \
		exit 1; \
	fi
	. $(VENV) && python3 -m alembic revision --autogenerate -m "$(message)"

# Apply migrations
migrate-up:
	@echo "Applying migrations..."
	. $(VENV) && python3 -m alembic upgrade head

# Rollback last migration
migrate-down:
	@echo "Rolling back last migration..."
	. $(VENV) && python3 -m alembic downgrade -1

# Clean up cache and temporary files
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 