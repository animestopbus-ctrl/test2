import logging
import asyncio
import sys
import signal
from datetime import datetime
from dotenv import load_dotenv

from telegram.ext import Application, CommandHandler
from telegram import __version__ as ptb_version

# Load environment variables
load_dotenv()

# Import configuration and modules
from config.config import (
    LASTPERSON07_TELEGRAM_TOKEN, LASTPERSON07_LOG_FORMAT,
    LASTPERSON07_LOG_FILE, LASTPERSON07_MESSAGES,
    LASTPERSON07_RATE_LIMIT_SECONDS
)
from db.client import lastperson07_db_client
from db.queries import lastperson07_queries
from utils.scheduler import lastperson07_init_scheduler
from utils.broadcaster import lastperson07_init_broadcaster
from handlers.user_handlers import lastperson07_register_user_handlers
from handlers.admin_handlers import lastperson07_register_admin_handlers
from handlers.error_handler import lastperson07_register_error_handler

# Setup logging
logging.basicConfig(
    format=LASTPERSON07_LOG_FORMAT,
    level=logging.INFO,
    handlers=[
        logging.FileHandler(LASTPERSON07_LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class LastPerson07Bot:
    """Main bot application class."""
    
    def __init__(self):
        """Initialize the bot."""
        self.application = None
        self.running = False
    
    async def lastperson07_initialize(self):
        """Initialize bot components."""
        try:
            # Log versions
            logger.info(f"Python version: {sys.version}")
            logger.info(f"python-telegram-bot version: {ptb_version}")
            
            # Connect to database
            logger.info("Connecting to database...")
            await lastperson07_db_client.connect()
            await lastperson07_db_client.create_indexes()
            
            # Create application
            logger.info("Creating Telegram application...")
            self.application = Application.builder().token(LASTPERSON07_TELEGRAM_TOKEN).build()
            
            # Initialize broadcaster
            logger.info("Initializing broadcaster...")
            lastperson07_init_broadcaster(self.application.bot)
            
            # Register handlers
            logger.info("Registering handlers...")
            lastperson07_register_user_handlers(self.application)
            lastperson07_register_admin_handlers(self.application)
            lastperson07_register_error_handler(self.application)
            
            # Initialize scheduler
            logger.info("Initializing scheduler...")
            await lastperson07_init_scheduler(self.application)
            
            # Check maintenance mode
            settings = await lastperson07_queries.get_bot_settings()
            if settings.maintenance:
                logger.warning("Bot is in maintenance mode")
            
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
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling(drop_pending_updates=True)
            
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
                from utils.scheduler import lastperson07_scheduler
                if lastperson07_scheduler:
                    await lastperson07_scheduler.stop()
                
                # Stop application
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
                
                # Close database connection
                await lastperson07_db_client.disconnect()
                
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
        # Setup signal handlers
        def signal_handler(sig, frame):
            logger.info("Received shutdown signal")
            asyncio.create_task(lastperson07_bot.lastperson07_stop())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start bot
        await lastperson07_bot.lastperson07_start()
        
        # Keep running
        while lastperson07_bot.running:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise
    finally:
        await lastperson07_bot.lastperson07_stop()
        logger.info("Bot shutdown complete")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        sys.exit(1)
