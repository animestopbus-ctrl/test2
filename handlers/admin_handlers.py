"""Admin Handlers for LastPerson07Bot

This module contains all admin-only command handlers.
"""

import logging
from typing import Optional, List

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler

from config.config import LASTPERSON07_OWNER_USER_ID
from db.queries import lastperson07_queries
from db.models import UserTier
from utils.stats import lastperson07_get_system_stats, lastperson07_format_db_stats

# Import at runtime to avoid circular imports
def get_broadcaster():
    from utils.broadcaster import lastperson07_broadcaster
    return lastperson07_broadcaster

def get_scheduler():
    from utils.scheduler import lastperson07_scheduler
    return lastperson07_scheduler

# Setup logging
logger = logging.getLogger(__name__)

class LastPerson07AdminHandlers:
    """Admin command handlers."""
    
    def __init__(self):
        """Initialize admin handlers."""
        pass
    
    async def lastperson07_check_admin(self, user_id: int) -> bool:
        """Check if user is admin."""
        settings = await lastperson07_queries.get_bot_settings()
        return user_id in settings.owners or user_id == LASTPERSON07_OWNER_USER_ID
    
    # ... rest of the handler methods remain the same, but update broadcaster calls:
    
    async def lastperson07_handle_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /broadcast command."""
        try:
            user_id = update.effective_user.id
            if not await self.lastperson07_check_admin(user_id):
                await update.message.reply_text("⛔ Admin access required")
                return
            
            if len(context.args) < 2:
                await update.message.reply_text("Usage: /broadcast group|channel|dm <message>")
                return
            
            broadcast_type = context.args[0].lower()
            message = " ".join(context.args[1:])
            
            broadcaster = get_broadcaster()
            
            if broadcast_type == "group":
                results = await broadcaster.lastperson07_broadcast_to_groups(message)
                await update.message.reply_text(f"✅ Broadcast sent to {results['success']}/{results['total']} groups")
            
            elif broadcast_type == "channel":
                # Need channel IDs from settings
                settings = await lastperson07_queries.get_bot_settings()
                channel_id = settings.bin_channel_id
                
                if channel_id:
                    await context.bot.send_message(chat_id=channel_id, text=message)
                    await update.message.reply_text("✅ Message sent to bin channel")
                else:
                    await update.message.reply_text("❌ No bin channel configured")
            
            elif broadcast_type == "dm":
                tier = context.args[1] if len(context.args) > 2 else "all"
                message = " ".join(context.args[2:]) if tier in ["free", "premium"] else message
                
                if tier == "free":
                    results = await broadcaster.lastperson07_broadcast_to_free_users(message)
                elif tier == "premium":
                    results = await broadcaster.lastperson07_broadcast_to_premium_users(message)
                else:
                    results = await broadcaster.lastperson07_broadcast_to_users(message)
                
                await update.message.reply_text(f"✅ Broadcast sent to {results['success']}/{results['total']} users")
            
            else:
                await update.message.reply_text("Usage: /broadcast group|channel|dm <message>")
                
        except Exception as e:
            logger.error(f"Error in broadcast handler: {str(e)}")
            await update.message.reply_text("An error occurred")

# Global handler instance
lastperson07_admin_handlers = LastPerson07AdminHandlers()

# Register handlers
def lastperson07_register_admin_handlers(application):
    """Register all admin handlers."""
    application.add_handler(CommandHandler("approve", lastperson07_admin_handlers.lastperson07_handle_approve))
    application.add_handler(CommandHandler("logs", lastperson07_admin_handlers.lastperson07_handle_logs))
    application.add_handler(CommandHandler("ban", lastperson07_admin_handlers.lastperson07_handle_ban))
    application.add_handler(CommandHandler("unban", lastperson07_admin_handlers.lastperson07_handle_unban))
    application.add_handler(CommandHandler("addpremium", lastperson07_admin_handlers.lastperson07_handle_addpremium))
    application.add_handler(CommandHandler("removepremium", lastperson07_admin_handlers.lastperson07_handle_removepremium))
    application.add_handler(CommandHandler("index", lastperson07_admin_handlers.lastperson07_handle_index))
    application.add_handler(CommandHandler("users", lastperson07_admin_handlers.lastperson07_handle_users))
    application.add_handler(CommandHandler("stats", lastperson07_admin_handlers.lastperson07_handle_stats))
    application.add_handler(CommandHandler("setnewapi", lastperson07_admin_handlers.lastperson07_handle_setnewapi))
    application.add_handler(CommandHandler("removeapi", lastperson07_admin_handlers.lastperson07_handle_removeapi))
    application.add_handler(CommandHandler("setdelays", lastperson07_admin_handlers.lastperson07_handle_setdelays))
    application.add_handler(CommandHandler("channellist", lastperson07_admin_handlers.lastperson07_handle_channellist))
    application.add_handler(CommandHandler("grouplist", lastperson07_admin_handlers.lastperson07_handle_grouplist))
    application.add_handler(CommandHandler("db", lastperson07_admin_handlers.lastperson07_handle_db))
    application.add_handler(CommandHandler("maintenance", lastperson07_admin_handlers.lastperson07_handle_maintenance))
    application.add_handler(CommandHandler("broadcast", lastperson07_admin_handlers.lastperson07_handle_broadcast))
    application.add_handler(CommandHandler("setbinchannel", lastperson07_admin_handlers.lastperson07_handle_setbinchannel))
