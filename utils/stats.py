"""Statistics Module for LastPerson07Bot

This module provides system and database statistics utilities.
"""

import logging
import sys
import platform
from datetime import datetime
from typing import Dict, Any
from telegram.ext import ContextTypes

from db.queries import lastperson07_queries

# Setup logging
logger = logging.getLogger(__name__)

async def lastperson07_get_system_stats() -> Dict[str, Any]:
    """Get comprehensive system statistics."""
    try:
        stats = await lastperson07_queries.get_statistics()
        
        # Add system info
        stats.update({
            "python_version": sys.version,
            "platform": platform.platform(),
            "bot_uptime": datetime.now().isoformat(),
            "memory_usage": "N/A"  # Could be implemented with psutil if needed
        })
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting system stats: {str(e)}")
        return {}

def lastperson07_format_db_stats(stats: Dict[str, Any]) -> str:
    """Format database statistics for display."""
    try:
        formatted = """*📊 Database Statistics*

👥 *Users:*
• Total: `{total_users}`
• Premium: `{premium_users}`
• Free: `{free_users}`
• Banned: `{banned_users}`

📤 *Activity:*
• Total Fetches: `{total_fetches}`
• Active Schedules: `{active_schedules}`

⏰ *System:*
• Python: `{python_version}`
• Platform: `{platform}`

✅ *Status: Running*"""
        
        return formatted.format(**stats)
        
    except Exception as e:
        logger.error(f"Error formatting DB stats: {str(e)}")
        return "*Error retrieving statistics*"

def lastperson07_format_user_info(user_data: Dict[str, Any]) -> str:
    """Format user information for display."""
    try:
        formatted = """*👤 User Information*

*ID:* `{user_id}`
*Username:* @{username}
*Name:* {first_name}
*Plan:* {plan}
*Today's Fetches:* {fetch_count}/{limit}
*Joined:* {join_date}
*Status:* {status}"""
        
        # Format values
        user_id = user_data.get("_id", "N/A")
        username = user_data.get("username", "N/A")
        first_name = user_data.get("first_name", "N/A")
        plan = user_data.get("tier", "free").title()
        fetch_count = user_data.get("fetch_count", 0)
        limit = "5" if user_data.get("tier", "free") == "free" else "∞"
        join_date = user_data.get("join_date", datetime.now()).strftime("%Y-%m-%d")
        status = "🟢 Active" if not user_data.get("banned", False) else "🔴 Banned"
        
        return formatted.format(
            user_id=user_id,
            username=username,
            first_name=first_name,
            plan=plan,
            fetch_count=fetch_count,
            limit=limit,
            join_date=join_date,
            status=status
        )
        
    except Exception as e:
        logger.error(f"Error formatting user info: {str(e)}")
        return "*Error retrieving user information*"

async def lastperson07_send_stats_to_channel(context: ContextTypes.DEFAULT_TYPE, 
                                           channel_id: int) -> bool:
    """Send statistics to a channel."""
    try:
        # Get stats
        stats = await lastperson07_get_system_stats()
        
        # Format message
        message = lastperson07_format_db_stats(stats)
        
        # Send to channel
        await context.bot.send_message(
            chat_id=channel_id,
            text=message,
            parse_mode="Markdown"
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Error sending stats to channel: {str(e)}")
        return False

def lastperson07_db_unicode_format() -> str:
    """Return exact unicode format for /db command."""
    return """┌──────────────────────────────────────┐
│         🗃️ DATABASE STATUS 🗃️         │
├──────────────────────────────────────┤
│  📊 Total Users:      1,234           │
│  💎 Premium Users:    56              │
│  👤 Free Users:       1,178           │
│  🚫 Banned Users:     12              │
│  📈 Total Fetches:    45,678          │
│  ⏰ Active Schedules: 8                │
│  🔄 Bot Uptime:       5d 14h 32m      │
└──────────────────────────────────────┘"""
