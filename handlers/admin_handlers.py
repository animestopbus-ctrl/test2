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
        try:
            settings = await lastperson07_queries.get_bot_settings()
            return user_id in settings.owners or user_id == LASTPERSON07_OWNER_USER_ID
        except Exception as e:
            logger.error(f"Error checking admin status: {str(e)}")
            return user_id == LASTPERSON07_OWNER_USER_ID  # Fallback check
    
    async def lastperson07_handle_approve(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /approve command."""
        try:
            user_id = update.effective_user.id
            if not await self.lastperson07_check_admin(user_id):
                await update.message.reply_text("⛔ Admin access required")
                return
            
            if not context.args:
                await update.message.reply_text("Usage: /approve <user_id>")
                return
            
            try:
                target_id = int(context.args[0])
            except ValueError:
                await update.message.reply_text("Invalid user ID")
                return
            
            # Unban user
            success = await lastperson07_queries.unban_user(target_id)
            
            if success:
                await update.message.reply_text(f"✅ User {target_id} has been approved")
            else:
                await update.message.reply_text("❌ Failed to approve user")
                
        except Exception as e:
            logger.error(f"Error in approve handler: {str(e)}")
            await update.message.reply_text("An error occurred")
    
    async def lastperson07_handle_logs(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /logs command."""
        try:
            user_id = update.effective_user.id
            if not await self.lastperson07_check_admin(user_id):
                await update.message.reply_text("⛔ Admin access required")
                return
            
            # Read recent logs
            try:
                with open("logs/bot.log", "r") as f:
                    logs = f.read()[-4000:]  # Last 4000 characters
                    if logs:
                        await update.message.reply_text(f"```\n{logs}\n```", parse_mode="MarkdownV2")
                    else:
                        await update.message.reply_text("No logs available")
            except FileNotFoundError:
                await update.message.reply_text("No log file found")
                
        except Exception as e:
            logger.error(f"Error in logs handler: {str(e)}")
            await update.message.reply_text("An error occurred")
    
    async def lastperson07_handle_ban(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /ban command."""
        try:
            user_id = update.effective_user.id
            if not await self.lastperson07_check_admin(user_id):
                await update.message.reply_text("⛔ Admin access required")
                return
            
            if not context.args:
                await update.message.reply_text("Usage: /ban <user_id>")
                return
            
            try:
                target_id = int(context.args[0])
            except ValueError:
                await update.message.reply_text("Invalid user ID")
                return
            
            success = await lastperson07_queries.ban_user(target_id)
            
            if success:
                await update.message.reply_text(f"✅ User {target_id} has been banned")
            else:
                await update.message.reply_text("❌ Failed to ban user")
                
        except Exception as e:
            logger.error(f"Error in ban handler: {str(e)}")
            await update.message.reply_text("An error occurred")
    
    async def lastperson07_handle_unban(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /unban command."""
        try:
            user_id = update.effective_user.id
            if not await self.lastperson07_check_admin(user_id):
                await update.message.reply_text("⛔ Admin access required")
                return
            
            if not context.args:
                await update.message.reply_text("Usage: /unban <user_id>")
                return
            
            try:
                target_id = int(context.args[0])
            except ValueError:
                await update.message.reply_text("Invalid user ID")
                return
            
            success = await lastperson07_queries.unban_user(target_id)
            
            if success:
                await update.message.reply_text(f"✅ User {target_id} has been unbanned")
            else:
                await update.message.reply_text("❌ Failed to unban user")
                
        except Exception as e:
            logger.error(f"Error in unban handler: {str(e)}")
            await update.message.reply_text("An error occurred")
    
    async def lastperson07_handle_addpremium(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /addpremium command."""
        try:
            user_id = update.effective_user.id
            if not await self.lastperson07_check_admin(user_id):
                await update.message.reply_text("⛔ Admin access required")
                return
            
            if not context.args:
                await update.message.reply_text("Usage: /addpremium <user_id>")
                return
            
            try:
                target_id = int(context.args[0])
            except ValueError:
                await update.message.reply_text("Invalid user ID")
                return
            
            success = await lastperson07_queries.upgrade_to_premium(target_id)
            
            if success:
                await update.message.reply_text(f"✅ User {target_id} upgraded to premium")
            else:
                await update.message.reply_text("❌ Failed to upgrade user")
                
        except Exception as e:
            logger.error(f"Error in addpremium handler: {str(e)}")
            await update.message.reply_text("An error occurred")
    
    async def lastperson07_handle_removepremium(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /removepremium command."""
        try:
            user_id = update.effective_user.id
            if not await self.lastperson07_check_admin(user_id):
                await update.message.reply_text("⛔ Admin access required")
                return
            
            if not context.args:
                await update.message.reply_text("Usage: /removepremium <user_id>")
                return
            
            try:
                target_id = int(context.args[0])
            except ValueError:
                await update.message.reply_text("Invalid user ID")
                return
            
            success = await lastperson07_queries.downgrade_to_free(target_id)
            
            if success:
                await update.message.reply_text(f"✅ User {target_id} downgraded to free")
            else:
                await update.message.reply_text("❌ Failed to downgrade user")
                
        except Exception as e:
            logger.error(f"Error in removepremium handler: {str(e)}")
            await update.message.reply_text("An error occurred")
    
    async def lastperson07_handle_index(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /index command."""
        try:
            user_id = update.effective_user.id
            if not await self.lastperson07_check_admin(user_id):
                await update.message.reply_text("⛔ Admin access required")
                return
            
            # Rebuild database indexes
            await lastperson07_db_client.create_indexes()
            await update.message.reply_text("✅ Database indexes rebuilt")
            
        except Exception as e:
            logger.error(f"Error in index handler: {str(e)}")
            await update.message.reply_text("An error occurred")
    
    async def lastperson07_handle_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /users command."""
        try:
            user_id = update.effective_user.id
            if not await self.lastperson07_check_admin(user_id):
                await update.message.reply_text("⛔ Admin access required")
                return
            
            users = await lastperson07_queries.get_all_users()
            
            message = f"*👥 Users ({len(users)})*\n\n"
            
            # Show recent 20 users
            for user in users[-20:]:
                status = "🚫" if user.get("banned", False) else "✅"
                tier = "💎" if user.get("tier") == "premium" else "👤"
                message += f"{status}{tier} {user.get('first_name', 'N/A')} (`{user['_id']}`)\n"
            
            await update.message.reply_text(message, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Error in users handler: {str(e)}")
            await update.message.reply_text("An error occurred")
    
    async def lastperson07_handle_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /stats command."""
        try:
            user_id = update.effective_user.id
            if not await self.lastperson07_check_admin(user_id):
                await update.message.reply_text("⛔ Admin access required")
                return
            
            stats = await lastperson07_get_system_stats()
            message = lastperson07_format_db_stats(stats)
            
            await update.message.reply_text(message, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Error in stats handler: {str(e)}")
            await update.message.reply_text("An error occurred")
    
    async def lastperson07_handle_setnewapi(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /setnewapi command."""
        try:
            user_id = update.effective_user.id
            if not await self.lastperson07_check_admin(user_id):
                await update.message.reply_text("⛔ Admin access required")
                return
            
            if len(context.args) < 2:
                await update.message.reply_text("Usage: /setnewapi <url> <source_name> [api_key]")
                return
            
            url = context.args[0]
            source_name = context.args[1]
            api_key = context.args[2] if len(context.args) > 2 else None
            
            success = await lastperson07_queries.add_api_url(url, source_name, api_key)
            
            if success:
                await update.message.reply_text("✅ New API added successfully")
            else:
                await update.message.reply_text("❌ Failed to add API")
                
        except Exception as e:
            logger.error(f"Error in setnewapi handler: {str(e)}")
            await update.message.reply_text("An error occurred")
    
    async def lastperson07_handle_removeapi(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /removeapi command."""
        try:
            user_id = update.effective_user.id
            if not await self.lastperson07_check_admin(user_id):
                await update.message.reply_text("⛔ Admin access required")
                return
            
            if not context.args:
                await update.message.reply_text("Usage: /removeapi <url>")
                return
            
            url = context.args[0]
            success = await lastperson07_queries.remove_api_url(url)
            
            if success:
                await update.message.reply_text("✅ API removed successfully")
            else:
                await update.message.reply_text("❌ Failed to remove API")
                
        except Exception as e:
            logger.error(f"Error in removeapi handler: {str(e)}")
            await update.message.reply_text("An error occurred")
    
    async def lastperson07_handle_setdelays(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /setdelays command."""
        try:
            user_id = update.effective_user.id
            if not await self.lastperson07_check_admin(user_id):
                await update.message.reply_text("⛔ Admin access required")
                return
            
            if not context.args:
                await update.message.reply_text("Usage: /setdelays <minutes>")
                return
            
            try:
                delay_minutes = int(context.args[0])
            except ValueError:
                await update.message.reply_text("Invalid number")
                return
            
            success = await lastperson07_queries.update_bot_settings({"delay_minutes": delay_minutes})
            
            if success:
                await update.message.reply_text(f"✅ Delay set to {delay_minutes} minutes")
            else:
                await update.message.reply_text("❌ Failed to update delay")
                
        except Exception as e:
            logger.error(f"Error in setdelays handler: {str(e)}")
            await update.message.reply_text("An error occurred")
    
    async def lastperson07_handle_channellist(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /channellist command."""
        try:
            user_id = update.effective_user.id
            if not await self.lastperson07_check_admin(user_id):
                await update.message.reply_text("⛔ Admin access required")
                return
            
            schedules = await lastperson07_queries.get_schedules()
            
            if not schedules:
                await update.message.reply_text("No channels scheduled")
                return
            
            message = "*📢 Scheduled Channels*\n\n"
            
            for schedule in schedules:
                status = "✅" if schedule.get("active", True) else "❌"
                message += f"{status} `{schedule['channel_id']}` - {schedule['interval']} - {schedule['category']}\n"
            
            await update.message.reply_text(message, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Error in channellist handler: {str(e)}")
            await update.message.reply_text("An error occurred")
    
    async def lastperson07_handle_grouplist(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /grouplist command."""
        try:
            user_id = update.effective_user.id
            if not await self.lastperson07_check_admin(user_id):
                await update.message.reply_text("⛔ Admin access required")
                return
            
            # Same as channellist for now
            await self.lastperson07_handle_channellist(update, context)
            
        except Exception as e:
            logger.error(f"Error in grouplist handler: {str(e)}")
            await update.message.reply_text("An error occurred")
    
    async def lastperson07_handle_db(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /db command."""
        try:
            user_id = update.effective_user.id
            if not await self.lastperson07_check_admin(user_id):
                await update.message.reply_text("⛔ Admin access required")
                return
            
            from utils.stats import lastperson07_db_unicode_format
            
            db_info = lastperson07_db_unicode_format()
            await update.message.reply_text(db_info)
            
        except Exception as e:
            logger.error(f"Error in db handler: {str(e)}")
            await update.message.reply_text("An error occurred")
    
    async def lastperson07_handle_maintenance(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /maintenance command."""
        try:
            user_id = update.effective_user.id
            if not await self.lastperson07_check_admin(user_id):
                await update.message.reply_text("⛔ Admin access required")
                return
            
            if not context.args:
                await update.message.reply_text("Usage: /maintenance on|off")
                return
            
            mode = context.args[0].lower()
            
            if mode not in ["on", "off"]:
                await update.message.reply_text("Usage: /maintenance on|off")
                return
            
            maintenance = mode == "on"
            success = await lastperson07_queries.update_bot_settings({"maintenance": maintenance})
            
            if success:
                status = "ON" if maintenance else "OFF"
                await update.message.reply_text(f"✅ Maintenance mode {status}")
            else:
                await update.message.reply_text("❌ Failed to update maintenance mode")
                
        except Exception as e:
            logger.error(f"Error in maintenance handler: {str(e)}")
            await update.message.reply_text("An error occurred")
    
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
    
    async def lastperson07_handle_setbinchannel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /setbinchannel command."""
        try:
            user_id = update.effective_user.id
            if not await self.lastperson07_check_admin(user_id):
                await update.message.reply_text("⛔ Admin access required")
                return
            
            if not context.args:
                await update.message.reply_text("Usage: /setbinchannel <channel_id>")
                return
            
            try:
                channel_id = int(context.args[0])
            except ValueError:
                await update.message.reply_text("Invalid channel ID")
                return
            
            success = await lastperson07_queries.update_bot_settings({"bin_channel_id": channel_id})
            
            if success:
                await update.message.reply_text(f"✅ Bin channel set to {channel_id}")
            else:
                await update.message.reply_text("❌ Failed to update bin channel")
                
        except Exception as e:
            logger.error(f"Error in setbinchannel handler: {str(e)}")
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
