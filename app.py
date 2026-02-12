"""Main Application for LastPerson07Bot

This module contains the main bot application setup and entry point.
"""

import logging
import asyncio
import sys
import signal
import os
from datetime import datetime
from dotenv import load_dotenv

# Setup basic logging before any imports
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables first
load_dotenv()

# Check required environment variables early
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_TOKEN not set in environment variables")
    sys.exit(1)

# Try to import telegram with fallback
try:
    from telegram.ext import Application, CommandHandler
    from telegram import __version__ as ptb_version
    PTB_AVAILABLE = True
    logger.info(f"Successfully imported python-telegram-bot v{ptb_version}")
except ImportError as e:
    logger.error(f"Failed to import telegram library: {e}")
    PTB_AVAILABLE = False
    sys.exit(1)

# Try to import configuration
try:
    from config.config import (
        LASTPERSON07_TELEGRAM_TOKEN, LASTPERSON07_LOG_FORMAT,
        LASTPERSON07_LOG_FILE, LASTPERSON07_MESSAGES,
        LASTPERSON07_RATE_LIMIT_SECONDS
    )
except ImportError as e:
    logger.error(f"Failed to import config: {e}")
    sys.exit(1)

# Import core modules with error handling
try:
    from db.client import lastperson07_db_client
    from db.queries import lastperson07_queries
except ImportError as e:
    logger.error(f"Failed to import database modules: {e}")
    sys.exit(1)

# Import utility modules with error handling
try:
    from utils.scheduler import lastperson07_init_scheduler
    from utils.broadcaster import lastperson07_init_broadcaster
except ImportError as e:
    logger.error(f"Failed to import utility modules: {e}")
    sys.exit(1)

# Import handlers with error handling
try:
    from handlers.user_handlers import lastperson07_register_user_handlers
    from handlers.admin_handlers import lastperson07_register_admin_handlers
    from handlers.error_handler import lastperson07_register_error_handler
except ImportError as e:
    logger.error(f"Failed to import handler modules: {e}")
    sys.exit(1)

# Setup logging configuration
def setup_logging():
    """Setup logging configuration."""
    try:
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)
        
        # Setup logging with both file and console output
        logging.basicConfig(
            format=LASTPERSON07_LOG_FORMAT,
            level=logging.INFO,
            handlers=[
                logging.FileHandler(LASTPERSON07_LOG_FILE),
                logging.StreamHandler(sys.stdout)
            ],
            force=True  # Override any existing logging config
        )
        
        logger.info("Logging configured successfully")
        return True
    except Exception as e:
        print(f"Failed to setup logging: {e}")
        return False

class LastPerson07Bot:
    """Main bot application class."""
    
    def __init__(self):
        """Initialize the bot."""
        self.application = None
        self.running = False
        self.scheduler_instance = None
    
    async def lastperson07_initialize(self):
        """Initialize bot components."""
        try:
            logger.info("Initializing LastPerson07Bot...")
            
            # Check required environment variables
            if not LASTPERSON07_TELEGRAM_TOKEN:
                logger.error("TELEGRAM_TOKEN not set in environment variables")
                raise ValueError("TELEGRAM_TOKEN is required")
            
            # Log versions
            logger.info(f"Python version: {sys.version}")
            logger.info(f"python-telegram-bot version: {ptb_version}")
            
            # Connect to database with retries
            max_retries = 5
            for i in range(max_retries):
                try:
                    logger.info(f"Connecting to database (attempt {i+1}/{max_retries})...")
                    await lastperson07_db_client.connect()
                    await lastperson07_db_client.create_indexes()
                    logger.info("Database connection established")
                    break
                except Exception as e:
                    if i == max_retries - 1:
                        logger.error(f"Failed to connect to database after {max_retries} attempts: {str(e)}")
                        raise
                    logger.warning(f"Database connection failed (attempt {i+1}): {str(e)}")
                    await asyncio.sleep(2 ** i)  # Exponential backoff
            
            # Create application
            logger.info("Creating Telegram application...")
            self.application = Application.builder().token(LASTPERSON07_TELEGRAM_TOKEN).build()
            
            # Initialize broadcaster
            try:
                logger.info("Initializing broadcaster...")
                lastperson07_init_broadcaster(self.application.bot)
                logger.info("Broadcaster initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize broadcaster: {str(e)}")
            
            # Register handlers
            try:
                logger.info("Registering handlers...")
                lastperson07_register_user_handlers(self.application)
                lastperson07_register_admin_handlers(self.application)
                lastperson07_register_error_handler(self.application)
                logger.info("Handlers registered")
            except Exception as e:
                logger.error(f"Failed to register handlers: {str(e)}")
                raise
            
            # Initialize scheduler
            try:
                logger.info("Initializing scheduler...")
                self.scheduler_instance = await lastperson07_init_scheduler(self.application)
                logger.info("Scheduler initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize scheduler: {str(e)}")
                # Don't fail completely if scheduler fails
            
            # Check maintenance mode
            try:
                settings = await lastperson07_queries.get_bot_settings()
                if settings.maintenance:
                    logger.warning("Bot is in maintenance mode")
            except Exception as e:
                logger.warning(f"Could not check maintenance mode: {str(e)}")
            
            logger.info("✅ Bot initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing bot: {str(e)}")
            raise
    
    async def lastperson07_start(self):
        """Start the bot."""
        try:
            if not self.application:
                await self.lastperson07_initialize()
            
            logger.info("Starting bot polling...")
            
            # Initialize application
            await self.application.initialize()
            await self.application.start()
            
            # Start polling with error handling
            try:
                await self.application.updater.start_polling(drop_pending_updates=True)
            except Exception as e:
                logger.error(f"Failed to start polling: {str(e)}")
                raise
            
            self.running = True
            logger.info("✅ Bot started successfully")
            
        except Exception as e:
            logger.error(f"Error starting bot: {str(e)}")
            raise
    
    async def lastperson07_stop(self):
        """Stop the bot gracefully."""
        try:
            if self.running and self.application:
                logger.info("Stopping bot...")
                
                # Stop scheduler
                if self.scheduler_instance:
                    try:
                        await self.scheduler_instance.stop()
                        logger.info("Scheduler stopped")
                    except Exception as e:
                        logger.warning(f"Error stopping scheduler: {str(e)}")
                
                # Stop application
                try:
                    await self.application.updater.stop()
                    await self.application.stop()
                    await self.application.shutdown()
                    logger.info("Application stopped")
                except Exception as e:
                    logger.warning(f"Error stopping application: {str(e)}")
                
                # Close database connection
                try:
                    await lastperson07_db_client.disconnect()
                    logger.info("Database connection closed")
                except Exception as e:
                    logger.warning(f"Error closing database: {str(e)}")
                
                self.running = False
                logger.info("✅ Bot stopped successfully")
                
        except Exception as e:
            logger.error(f"Error stopping bot: {str(e)}")

class LastPerson07RateLimiter:
    """Simple rate limiter for user commands."""
    
    def __init__(self):
        self.user_timestamps = {}
    
    async def check_rate_limit(self, user_id: int) -> bool:
        """Check if user is rate limited."""
        import time
        
        now = time.time()
        last_time = self.user_timestamps.get(user_id, 0)
        
        if now - last_time < LASTPERSON07_RATE_LIMIT_SECONDS:
            return False
        
        self.user_timestamps[user_id] = now
        return True

# Global instances
lastperson07_bot = LastPerson07Bot()
lastperson07_rate_limiter = LastPerson07RateLimiter()

async def main():
    """Main entry point."""
    try:
        # Setup logging first
        if not setup_logging():
            print("Failed to setup logging")
            sys.exit(1)
        
        # Setup signal handlers
        def signal_handler(sig, frame):
            logger.info("Received shutdown signal")
            # Create task to stop bot gracefully
            if lastperson07_bot.running:
                asyncio.create_task(lastperson07_bot.lastperson07_stop())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start bot
        await lastperson07_bot.lastperson07_start()
        
        # Keep running
        logger.info("Bot is running. Press Ctrl+C to stop.")
        while lastperson07_bot.running:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        logger.exception("Full traceback:")
        raise
    finally:
        if lastperson07_bot.running:
            await lastperson07_bot.lastperson07_stop()
        logger.info("Bot shutdown complete")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        sys.exit(1)
