"""Error Handler for LastPerson07Bot

This module provides global error handling for the bot.
"""

import logging
import traceback
from telegram import Update
from telegram.ext import ContextTypes

from config.config import LASTPERSON07_MESSAGES, LASTPERSON07_OWNER_USER_ID
from db.client import lastperson07_db_client

# Setup logging
logger = logging.getLogger(__name__)

async def lastperson07_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the bot."""
    logger.error("Exception while handling an update:", exc_info=context.error)
    
    # Get the error
    error = context.error
    
    # Log the error details
    logger.error(f"Update: {update}")
    logger.error(f"Error: {str(error)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    # Try to notify user
    try:
        if isinstance(update, Update) and update.effective_message:
            await update.effective_message.reply_text(
                LASTPERSON07_MESSAGES["fetch_error"]
            )
    except:
        pass
    
    # Try to send error to admin
    try:
        error_message = f"⚠️ Bot Error\n\nError: {str(error)}\n\nUpdate: {str(update)[:200]}"
        
        if LASTPERSON07_OWNER_USER_ID:
            await context.bot.send_message(
                chat_id=LASTPERSON07_OWNER_USER_ID,
                text=error_message
            )
    except:
        pass
    
    # Try to log to database
    try:
        await lastperson07_db_client.insert_one("error_logs", {
            "error": str(error),
            "update": str(update),
            "traceback": traceback.format_exc(),
            "timestamp": datetime.now()
        })
    except:
        pass

def lastperson07_register_error_handler(application):
    """Register the global error handler."""
    application.add_error_handler(lastperson07_error_handler)
