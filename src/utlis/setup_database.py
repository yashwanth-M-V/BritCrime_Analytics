#!/usr/bin/env python3
"""
Initial database setup script
Run this first to initialize the SQLite database
"""

import logging
from core.sqlite_manager import db_manager
from core.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Initialize the database"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting database setup...")
        
        # Create directories
        config.setup_directories()
        logger.info("Project directories created")
        
        # Initialize database
        db_manager.initialize_database()
        logger.info("Database setup completed successfully")
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        raise

if __name__ == "__main__":
    main()