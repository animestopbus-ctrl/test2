"""User Handlers for LastPerson07Bot

This module contains all user-facing command handlers.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from config.config import (
    LASTPERSON07_MESSAGES, LASTPERSON07_CATEGORIES,
    LASTPERSON07_FREE_FETCH_LIMIT, LASTPERSON07_OWNER_USERNAME
)
from db.queries import lastperson07_queries
from db.models import UserTier
from utils.fetcher import lastperson07_wallpaper_fetcher
from utils.promoter import (
    lastperson07_add_promo_button_if_free,
    lastperson07_create_main_menu_keyboard,
    lastperson07_create_category_keyboard,
    lastperson07_create_premium_keyboard
)
from utils.metadata import lastperson07_format_wallpaper_caption

# Import reactions with fallback
try:
    from utils.reactions import (
        lastperson07_add_reaction_to_user_message, 
        lastperson07_add_reaction_to_bot_message
    )
    REACTIONS_AVAILABLE = True
except ImportError:
    logging.getLogger(__name__).warning("Reactions module not available, continuing without reactions")
    REACTIONS_AVAILABLE = False
    async def lastperson07_add_reaction_to_user_message(*args, **kwargs):
        pass
    async def lastperson07_add_reaction_to_bot_message(*args, **kwargs):
        pass

# Setup logging
logger = logging.getLogger(__name__)

class LastPerson07UserHandlers:
    """User command handlers."""
    
    def __init__(self):
        """Initialize user handlers."""
        self.rate_limit_cache = {}
    
    async def lastperson07_handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        try:
            # Add reaction with fallback
            if REACTIONS_AVAILABLE:
                await lastperson07_add_reaction_to_user_message(update, context)
            
            # Get or create user
            user = update.effective_user
            db_user = await lastperson07_queries.get_user(user.id)
            
            if db_user is None:
                await lastperson07_queries.create_user(
                    user_id=user.id,
                    username=user.username,
                    first_name=user.first_name
                )
                db_user = await lastperson07_queries.get_user(user.id)
            
            # Send welcome message
            keyboard = lastperson07_create_main_menu_keyboard()
            
            await update.message.reply_text(
                LASTPERSON07_MESSAGES["welcome"],
                parse_mode="Markdown",
                reply_markup=keyboard
            )
            
        except Exception as e:
            logger.error(f"Error in start handler: {str(e)}")
            await update.message.reply_text(LASTPERSON07_MESSAGES["invalid_command"])
    
    async def lastperson07_handle_fetch(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /fetch command."""
        try:
            # Add reaction with fallback
            if REACTIONS_AVAILABLE:
                await lastperson07_add_reaction_to_user_message(update, context)
            
            # Get user
            user = update.effective_user
            db_user = await lastperson07_queries.get_user(user.id)
            
            if db_user is None:
                await lastperson07_queries.create_user(
                    user_id=user.id,
                    username=user.username,
                    first_name=user.first_name
                )
                db_user = await lastperson07_queries.get_user(user.id)
            
            # Check if banned
            if db_user is not None and db_user.banned:
                await update.message.reply_text(LASTPERSON07_MESSAGES["banned"])
                return
            
            # Check daily limit
            reached_limit, remaining = await lastperson07_queries.check_daily_limit(user.id)
            
            if reached_limit and db_user.tier == UserTier.FREE:
                await update.message.reply_text(
                    LASTPERSON07_MESSAGES["daily_limit"].format(limit=LASTPERSON07_FREE_FETCH_LIMIT)
                )
                return
            
            # Get category
            category = LASTPERSON07_CATEGORIES[0]  # Default
            if context.args:
                category = context.args[0]
            
            # Fetch wallpaper
            wallpaper_data = await lastperson07_wallpaper_fetcher.fetch_wallpaper(category)
            
            if wallpaper_data is None:
                await update.message.reply_text(LASTPERSON07_MESSAGES["fetch_error"])
                return
            
            # Format caption
            caption = lastperson07_format_wallpaper_caption(wallpaper_data)
            
            # Create keyboard
            keyboard = []
            
            # Add download button
            if wallpaper_data.download_url:
                keyboard.append([InlineKeyboardButton("⬇️ Download", url=wallpaper_data.download_url)])
            
            # Add promo button for free users
            reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
            reply_markup = await lastperson07_add_promo_button_if_free(update, context, reply_markup)
            
            # Send photo
            sent_message = await update.message.reply_photo(
                photo=wallpaper_data.image_url,
                caption=caption,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            
            # Add reaction to bot message with fallback
            if REACTIONS_AVAILABLE:
                try:
                    await lastperson07_add_reaction_to_bot_message(context, update.effective_chat.id, sent_message.message_id)
                except Exception as e:
                    logger.debug(f"Could not add reaction: {str(e)}")
                    # Continue even if reaction fails
            
            # Update fetch count
            await lastperson07_queries.update_user_fetch_count(user.id)
            
        except Exception as e:
            logger.error(f"Error in fetch handler: {str(e)}")
            await update.message.reply_text(LASTPERSON07_MESSAGES["fetch_error"])
    
    async def lastperson07_handle_myplan(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /myplan command."""
        try:
            if REACTIONS_AVAILABLE:
                await lastperson07_add_reaction_to_user_message(update, context)
            
            user = update.effective_user
            db_user = await lastperson07_queries.get_user(user.id)
            
            if db_user is None:
                await update.message.reply_text("Please use /start first")
                return
            
            # Check daily limit
            reached_limit, remaining = await lastperson07_queries.check_daily_limit(user.id)
            
            if db_user.tier == UserTier.PREMIUM:
                message = "*✨ Premium Plan*\n\nYou have unlimited access to wallpapers!"
            else:
                message = f"*ℹ️ Free Plan*\n\nDaily limit: {LASTPERSON07_FREE_FETCH_LIMIT - remaining}/{LASTPERSON07_FREE_FETCH_LIMIT} used"
            
            await update.message.reply_text(message, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Error in myplan handler: {str(e)}")
    
    async def lastperson07_handle_premium(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /premium command."""
        try:
            if REACTIONS_AVAILABLE:
                await lastperson07_add_reaction_to_user_message(update, context)
            
            keyboard = lastperson07_create_premium_keyboard()
            
            await update.message.reply_text(
                LASTPERSON07_MESSAGES["premium_info"],
                parse_mode="Markdown",
                reply_markup=keyboard
            )
            
        except Exception as e:
            logger.error(f"Error in premium handler: {str(e)}")
    
    async def lastperson07_handle_buy(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /buy command."""
        try:
            if REACTIONS_AVAILABLE:
                await lastperson07_add_reaction_to_user_message(update, context)
            
            contact_button = InlineKeyboardButton(
                "Contact Owner to Buy",
                url=f"https://t.me/{LASTPERSON07_OWNER_USERNAME}"
            )
            keyboard = InlineKeyboardMarkup([[contact_button]])
            
            await update.message.reply_text(
                "To purchase premium, contact the owner:",
                reply_markup=keyboard
            )
            
        except Exception as e:
            logger.error(f"Error in buy handler: {str(e)}")
    
    async def lastperson07_handle_categories(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /categories command."""
        try:
            if REACTIONS_AVAILABLE:
                await lastperson07_add_reaction_to_user_message(update, context)
            
            categories_list = "\n".join([f"• {cat.title()}" for cat in LASTPERSON07_CATEGORIES])
            
            await update.message.reply_text(
                LASTPERSON07_MESSAGES["categories"].format(categories_list=categories_list),
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error in categories handler: {str(e)}")
    
    async def lastperson07_handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command."""
        try:
            if REACTIONS_AVAILABLE:
                await lastperson07_add_reaction_to_user_message(update, context)
            
            categories_list = "\n".join([f"• {cat.title()}" for cat in LASTPERSON07_CATEGORIES])
            
            await update.message.reply_text(
                LASTPERSON07_MESSAGES["help"].format(
                    categories_list=categories_list,
                    owner=LASTPERSON07_OWNER_USERNAME
                ),
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error in help handler: {str(e)}")
    
    async def lastperson07_handle_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /info command."""
        try:
            if REACTIONS_AVAILABLE:
                await lastperson07_add_reaction_to_user_message(update, context)
            
            info_text = f"""*🤖 LastPerson07 Wallpaper Bot*

*Version:* 1.0.0
*Description:* Fetch beautiful wallpapers from multiple sources

*Features:*
• High-quality wallpapers (≥1920×1080)
• Multiple categories
• Free and premium tiers
• Scheduled posting

*APIs:*
• Unsplash
• Pexels
• Pixabay

*Contact:* @{LASTPERSON07_OWNER_USERNAME}"""
            
            await update.message.reply_text(info_text, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Error in info handler: {str(e)}")
    
    async def lastperson07_handle_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /report command."""
        try:
            if REACTIONS_AVAILABLE:
                await lastperson07_add_reaction_to_user_message(update, context)
            
            if not context.args:
                await update.message.reply_text("Usage: /report <issue description>")
                return
            
            report_text = " ".join(context.args)
            
            # Log report
            logger.warning(f"User report from {update.effective_user.id}: {report_text}")
            
            await update.message.reply_text("✅ Your report has been sent to the admin.")
            
        except Exception as e:
            logger.error(f"Error in report handler: {str(e)}")
    
    async def lastperson07_handle_feedback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /feedback command."""
        try:
            if REACTIONS_AVAILABLE:
                await lastperson07_add_reaction_to_user_message(update, context)
            
            if not context.args:
                await update.message.reply_text("Usage: /feedback <your feedback>")
                return
            
            feedback_text = " ".join(context.args)
            
            # Log feedback
            logger.info(f"User feedback from {update.effective_user.id}: {feedback_text}")
            
            await update.message.reply_text("✅ Thank you for your feedback!")
            
        except Exception as e:
            logger.error(f"Error in feedback handler: {str(e)}")
    
    async def lastperson07_handle_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /schedule command."""
        try:
            if REACTIONS_AVAILABLE:
                await lastperson07_add_reaction_to_user_message(update, context)
            
            user = update.effective_user
            db_user = await lastperson07_queries.get_user(user.id)
            
            if db_user is None:
                await update.message.reply_text("Please use /start first")
                return
            
            # Check if user is admin
            from handlers.admin_handlers import lastperson07_admin_handlers
            if not await lastperson07_admin_handlers.lastperson07_check_admin(user.id):
                await update.message.reply_text("⛔ Admin access required")
                return
            
            if not context.args or len(context.args) < 2:
                await update.message.reply_text("Usage: /schedule <interval> <category>")
                return
            
            interval = context.args[0].lower()
            category = context.args[1]
            
            if interval not in ["hourly", "daily"]:
                await update.message.reply_text("Interval must be 'hourly' or 'daily'")
                return
            
            # Create schedule
            chat_id = update.effective_chat.id
            success = await lastperson07_queries.create_schedule(chat_id, interval, category)
            
            if success:
                await update.message.reply_text(f"✅ Schedule created: {interval} posts of {category}")
            else:
                await update.message.reply_text("❌ Failed to create schedule")
                
        except Exception as e:
            logger.error(f"Error in schedule handler: {str(e)}")
            await update.message.reply_text("An error occurred")
    
    async def lastperson07_handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle callback queries from inline keyboards."""
        try:
            query = update.callback_query
            await query.answer()
            
            data = query.data
            
            if data == "main_menu":
                keyboard = lastperson07_create_main_menu_keyboard()
                await query.edit_message_text(
                    "Choose an option:",
                    reply_markup=keyboard
                )
            
            elif data == "fetch_menu":
                keyboard = lastperson07_create_category_keyboard(LASTPERSON07_CATEGORIES)
                await query.edit_message_text(
                    "Choose a category:",
                    reply_markup=keyboard
                )
            
            elif data.startswith("fetch_"):
                category = data.replace("fetch_", "")
                
                # Send typing action using query.bot instead of query.message.bot
                await query.bot.send_chat_action(chat_id=query.message.chat_id, action="typing")
                
                # Fetch wallpaper
                wallpaper_data = await lastperson07_wallpaper_fetcher.fetch_wallpaper(category)
                
                if wallpaper_data is not None:
                    caption = lastperson07_format_wallpaper_caption(wallpaper_data)
                    
                    # Create keyboard
                    keyboard = []
                    if wallpaper_data.download_url:
                        keyboard.append([InlineKeyboardButton("⬇️ Download", url=wallpaper_data.download_url)])
                    
                    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
                    reply_markup = await lastperson07_add_promo_button_if_free(update, context, reply_markup)
                    
                    # Send photo
                    sent_message = await query.bot.send_photo(
                        chat_id=query.message.chat_id,
                        photo=wallpaper_data.image_url,
                        caption=caption,
                        parse_mode="Markdown",
                        reply_markup=reply_markup
                    )
                    
                    # Add reaction with fallback
                    if REACTIONS_AVAILABLE:
                        try:
                            await lastperson07_add_reaction_to_bot_message(context, query.message.chat_id, sent_message.message_id)
                        except Exception as e:
                            logger.debug(f"Could not add reaction: {str(e)}")
                            # Continue even if reaction fails
                    
                    # Update user fetch count
                    await lastperson07_queries.update_user_fetch_count(query.from_user.id)
                else:
                    await query.edit_message_text("Failed to fetch wallpaper. Please try again.")
            
            elif data == "categories":
                categories_list = "\n".join([f"• {cat.title()}" for cat in LASTPERSON07_CATEGORIES])
                await query.edit_message_text(
                    LASTPERSON07_MESSAGES["categories"].format(categories_list=categories_list),
                    parse_mode="Markdown"
                )
            
            elif data == "myplan":
                user = query.from_user
                db_user = await lastperson07_queries.get_user(user.id)
                
                if db_user is not None and db_user.tier == UserTier.PREMIUM:
                    message = "*✨ Premium Plan*\n\nYou have unlimited access to wallpapers!"
                else:
                    reached_limit, remaining = await lastperson07_queries.check_daily_limit(user.id)
                    message = f"*ℹ️ Free Plan*\n\nDaily limit: {LASTPERSON07_FREE_FETCH_LIMIT - remaining}/{LASTPERSON07_FREE_FETCH_LIMIT} used"
                
                await query.edit_message_text(message, parse_mode="Markdown")
            
            elif data == "premium_info":
                await query.edit_message_text(
                    LASTPERSON07_MESSAGES["premium_info"],
                    parse_mode="Markdown",
                    reply_markup=lastperson07_create_premium_keyboard()
                )
            
            elif data == "help":
                categories_list = "\n".join([f"• {cat.title()}" for cat in LASTPERSON07_CATEGORIES])
                await query.edit_message_text(
                    LASTPERSON07_MESSAGES["help"].format(
                        categories_list=categories_list,
                        owner=LASTPERSON07_OWNER_USERNAME
                    ),
                    parse_mode="Markdown"
                )
            
        except Exception as e:
            logger.error(f"Error in callback query handler: {str(e)}")
            if update.callback_query:
                await update.callback_query.answer("An error occurred", show_alert=True)

# Global handler instance
lastperson07_user_handlers = LastPerson07UserHandlers()

# Register handlers
def lastperson07_register_user_handlers(application):
    """Register all user handlers."""
    application.add_handler(CommandHandler("start", lastperson07_user_handlers.lastperson07_handle_start))
    application.add_handler(CommandHandler("fetch", lastperson07_user_handlers.lastperson07_handle_fetch))
    application.add_handler(CommandHandler("myplan", lastperson07_user_handlers.lastperson07_handle_myplan))
    application.add_handler(CommandHandler("premium", lastperson07_user_handlers.lastperson07_handle_premium))
    application.add_handler(CommandHandler("buy", lastperson07_user_handlers.lastperson07_handle_buy))
    application.add_handler(CommandHandler("categories", lastperson07_user_handlers.lastperson07_handle_categories))
    application.add_handler(CommandHandler("help", lastperson07_user_handlers.lastperson07_handle_help))
    application.add_handler(CommandHandler("info", lastperson07_user_handlers.lastperson07_handle_info))
    application.add_handler(CommandHandler("report", lastperson07_user_handlers.lastperson07_handle_report))
    application.add_handler(CommandHandler("feedback", lastperson07_user_handlers.lastperson07_handle_feedback))
    application.add_handler(CommandHandler("schedule", lastperson07_user_handlers.lastperson07_handle_schedule))
    application.add_handler(CallbackQueryHandler(lastperson07_user_handlers.lastperson07_handle_callback_query))
