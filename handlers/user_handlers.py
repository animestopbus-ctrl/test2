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
            
            if not db_user:
                await lastperson07_queries.create_user(
                    user_id=user.id,
                    username=user.username,
                    first_name=user.first_name
                )
            
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
            
            if not db_user:
                await lastperson07_queries.create_user(
                    user_id=user.id,
                    username=user.username,
                    first_name=user.first_name
                )
                db_user = await lastperson07_queries.get_user(user.id)
            
            # Check if banned
            if db_user.banned:
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
            
            if not wallpaper_data:
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
            
            if not db_user:
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
                "
