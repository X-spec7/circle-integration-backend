"""
Logging configuration for the application
"""
import logging
import sys

def setup_logging():
    """Setup application logging with proper configuration"""
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    # Setup specific loggers
    logging.getLogger("app").setLevel(logging.INFO)
    logging.getLogger("app.services").setLevel(logging.INFO)
    logging.getLogger("app.services.blockchain_service").setLevel(logging.INFO)
    logging.getLogger("app.services.project_service").setLevel(logging.INFO)
    
    # Reduce uvicorn access logs
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    print("🔧 Logging configured successfully")

# Setup logging when this module is imported
setup_logging()
