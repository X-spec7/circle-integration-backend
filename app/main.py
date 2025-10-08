# Import logging configuration first
from contextlib import asynccontextmanager
import logging_config

import logging
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.api.v1.api import api_router
from app.services.event_listener import live_event_listener

def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title=settings.app_name,
        description="A scalable FastAPI backend with authentication and user management",
        version=settings.app_version,
        debug=settings.debug,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API router
    app.include_router(api_router, prefix=settings.api_prefix)
    
    return app

# Create application instance
app = create_application()

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and start blockchain event syncing on app startup."""
    # Startup logic
    init_db()
    try:
        await live_event_listener.start()
    except Exception as e:
        logger.error(f"Failed to start live event listener: {e}")

    # Yield control back to FastAPI
    yield

    # Shutdown logic (optional)
    try:
        await live_event_listener.stop()
    except Exception as e:
        logger.error(f"Failed to stop live event listener: {e}")

@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc"
    }
