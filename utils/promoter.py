

import logging
from typing import Optional, List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

# Import needed constants
from config.config import (
    LASTPERSON07_PROMO_CHANNEL, 
    LASTPERSON07_OWNER_USERNAME  # This was missing
)
from db.models import UserTier
from db.queries import lastperson07_queries

# Setup logging
logger = logging.getLogger(__name__)

async def lastperson07_add_promo_button_if_free(update: Update, 
                                               context: ContextTypes.DEFAULT_TYPE,
                                               reply_markup: Optional[InlineKeyboardMarkup] = None) -> Optional[InlineKeyboardMarkup]:
    """Add promotional button for free users."""
    try:
        # Get user
        user_id = update.effective_user.id
        user = await lastperson07_queries.get_user(user_id)
        
        if not user or user.tier == UserTier.FREE:
            # Create keyboard with promo button
            keyboard = []
            
            if reply_markup and reply_markup.inline_keyboard:
                # Add to existing keyboard
                for row in reply_markup.inline_keyboard:
                    keyboard.append(row)
            
            # Add promo button
            promo_button = InlineKeyboardButton(
                "Join Channel 😁",
                url=f"https://t.me/{LASTPERSON07_PROMO_CHANNEL}"
            )
            keyboard.append([promo_button])
            
            return InlineKeyboardMarkup(keyboard)
        
        # Return original keyboard for premium users
        return reply_markup
        
    except Exception as e:
        logger.error(f"Error adding promo button: {str(e)}")
        return reply_markup

def lastperson07_create_premium_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard with premium purchase options."""
    keyboard = [
        [InlineKeyboardButton("💎 Get Premium", callback_data="premium_info")],
        [InlineKeyboardButton("💳 Contact Owner", url=f"https://t.me/{LASTPERSON07_OWNER_USERNAME}")]
    ]
    return InlineKeyboardMarkup(keyboard)

def lastperson07_create_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Create main menu keyboard."""
    keyboard = [
        [InlineKeyboardButton("🖼️ Fetch Wallpaper", callback_data="fetch_menu")],
        [InlineKeyboardButton("💎 My Plan", callback_data="myplan")],
        [InlineKeyboardButton("📁 Categories", callback_data="categories")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)

def lastperson07_create_category_keyboard(categories: List[str]) -> InlineKeyboardMarkup:
    """Create keyboard with categories."""
    keyboard = []
    
    # Create rows of 2 buttons each
    for i in range(0, len(categories), 2):
        row = []
        if i < len(categories):
            row.append(InlineKeyboardButton(
                categories[i].title(), 
                callback_data=f"fetch_{categories[i]}"
            ))
        if i + 1 < len(categories):
            row.append(InlineKeyboardButton(
                categories[i + 1].title(), 
                callback_data=f"fetch_{categories[i + 1]}"
            ))
        keyboard.append(row)
    
    # Add back button
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(keyboard)

async def lastperson07_send_promo_message(update: Update, 
                                        context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send promotional message to user."""
    try:
        promo_text = """*✨ Upgrade to Premium Today!*

Enjoy unlimited wallpapers with:
• No daily limits
• No promotional buttons
• Priority support
• Early access to new features

💳 *Pricing:*
• 1 Month: $5
• 3 Months: $12
• 6 Months: $20

Click below to purchase now!"""
        
        keyboard = lastperson07_create_premium_keyboard()
        
        await update.message.reply_text(
            promo_text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Error sending promo message: {str(e)}")
