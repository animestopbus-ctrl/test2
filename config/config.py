"""LastPerson07Bot Configuration Module

This module contains all configuration settings, constants, API endpoints,
message templates, and other shared configuration data for the bot.
"""

import os
from typing import List, Dict, Any
from dataclasses import dataclass

# Environment Variables
LASTPERSON07_TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
LASTPERSON07_MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/lastperson07")
LASTPERSON07_UNSPLASH_KEY = os.getenv("UNSPLASH_KEY")
LASTPERSON07_PEXELS_KEY = os.getenv("PEXELS_KEY")
LASTPERSON07_PIXABAY_KEY = os.getenv("PIXABAY_KEY")
LASTPERSON07_OWNER_USERNAME = os.getenv("OWNER_USERNAME")
LASTPERSON07_PROMO_CHANNEL = os.getenv("PROMO_CHANNEL")
LASTPERSON07_OWNER_USER_ID = int(os.getenv("OWNER_USER_ID", "0"))

# API Endpoints
LASTPERSON07_API_ENDPOINTS = {
    "unsplash": "https://api.unsplash.com/photos/random",
    "pexels": "https://api.pexels.com/v1/search",
    "pixabay": "https://pixabay.com/api/"
}

# Bot Settings
LASTPERSON07_FREE_FETCH_LIMIT = 5
LASTPERSON07_RATE_LIMIT_SECONDS = 2
LASTPERSON07_DEFAULT_DELAY_MINUTES = 5
LASTPERSON07_MIN_IMAGE_WIDTH = 1920
LASTPERSON07_MIN_IMAGE_HEIGHT = 1080
LASTPERSON07_MAX_FILE_SIZE_MB = 20

# Emoji Reactions Pool
LASTPERSON07_REACTIONS = [
    "👍", "❤️", "🔥", "🥰", "👏", "😁", "🤔", "🤯", "😱", "🤬",
    "😢", "🎉", "🤩", "🤮", "💩", "🙏", "👌", "🕊", "🤡", "🥱",
    "🥴", "😍", "🐳", "❤️‍🔥", "🌚", "🌭", "💯", "🤣", "⚡", "🍌",
    "🏆", "💔", "🤨", "😐", "🍓", "🍾", "💋", "🖕", "😈", "😴",
    "😭", "🤓", "👻", "👨‍💻", "👀", "🎃", "🙈", "😇", "😨", "🤝",
    "✍", "🤗", "🫡", "🎅", "🎄", "☃", "💅", "🤪", "🗿", "🆒",
    "💘", "🙉", "🦄", "😘", "💊", "🙊", "😎", "👾", "🤷‍♂️", "🤷‍♀️",
    "😡"
]

# Categories
LASTPERSON07_CATEGORIES = [
    "nature", "city", "animals", "abstract", "technology",
    "food", "people", "objects", "buildings", "travel",
    "flowers", "beach", "mountains", "sunset", "space",
    "cars", "fashion", "sports", "music", "art"
]

# Message Templates
LASTPERSON07_MESSAGES = {
    "welcome": """*🎉 Welcome to LastPerson07 Wallpaper Bot!*

I fetch beautiful wallpapers from multiple sources just for you!

📸 *Features:*
• High-quality wallpapers (≥1920×1080)
• 20+ categories to choose from
• Free users: 5 wallpapers per day
• Premium users: Unlimited wallpapers

🚀 *Commands:*
/start - Start the bot
/fetch <category> - Get a wallpaper
/myplan - Check your subscription
/premium - Upgrade to premium
/categories - View all categories
/help - Show help message

*Start with:* /fetch nature""",
    
    "fetch_usage": """*⚠️ Usage:* /fetch <category>

*Available categories:*
{categories}

*Example:* /fetch nature""",
    
    "daily_limit": """*⛔ Daily Limit Reached!*

You've used your {limit} free wallpapers for today.

*Upgrade to Premium for unlimited access:*
• No daily limits
• No promotional buttons
• Priority support

/buy - View premium plans""",
    
    "premium_info": """*✨ Premium Subscription*

*Benefits:*
🔥 Unlimited wallpaper fetching
🚫 No promotional buttons
⚡ Faster response times
📞 Priority support

*Pricing:*
• 1 Month: $5
• 3 Months: $12
• 6 Months: $20

*How to buy:*
Click the button below to contact the owner for payment

/buy - Contact owner to purchase""",
    
    "categories": """*📁 Available Categories:*

{categories_list}

*Usage:* /fetch <category>""",
    
    "help": """*🤖 LastPerson07 Bot Help*

*User Commands:*
/start - Welcome message
/fetch <cat> - Get wallpaper
/myplan - Check your plan
/premium - View premium info
/buy - Purchase premium
/categories - List categories
/info - Bot information
/report <text> - Report issues
/feedback <text> - Send feedback

*Rate Limits:*
• Free users: 5 wallpapers/day
• Premium users: Unlimited

*Categories:*
{categories_list}

*Need help?* Contact: @{owner}""",
    
    "maintenance": "*🔧 Maintenance Mode*\n\nBot is under maintenance. Please try again later.",
    "invalid_command": "*❌ Invalid Command*\n\nPlease use /help to see available commands.",
    "fetch_error": "*⚠️ Error Fetching Wallpaper*\n\nPlease try again in a moment.",
    "rate_limit": "*⏳ Please Wait*\n\nYou can send one command every 2 seconds.",
    "banned": "*🚫 Access Denied*\n\nYour account has been banned from using this bot."
}

# Database Settings
LASTPERSON07_DB_NAME = "lastperson07"
LASTPERSON07_COLLECTIONS = {
    "users": "users",
    "api_urls": "api_urls",
    "schedules": "schedules",
    "bot_settings": "bot_settings"
}

# Logging Configuration
LASTPERSON07_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LASTPERSON07_LOG_FILE = "logs/bot.log"
