"""Broadcaster Module for LastPerson07Bot

This module handles broadcasting messages to groups, channels, and users.
"""

import logging
import asyncio
from typing import List, Dict, Any
from telegram import Bot
from telegram.ext import ContextTypes

from db.queries import lastperson07_queries

# Setup logging
logger = logging.getLogger(__name__)

class LastPerson07Broadcaster:
    """Handles broadcasting messages to various destinations."""
    
    def __init__(self, bot: Bot):
        """Initialize broadcaster with bot instance."""
        self.bot = bot
    
    async def lastperson07_broadcast_to_groups(self, message: str, delay: float = 1.0) -> Dict[str, Any]:
        """Broadcast message to all active schedules (groups/channels)."""
        try:
            schedules = await lastperson07_queries.get_schedules(active_only=True)
            
            results = {
                "total": len(schedules),
                "success": 0,
                "failed": 0,
                "details": []
            }
            
            for schedule in schedules:
                try:
                    await self.bot.send_message(
                        chat_id=schedule["channel_id"],
                        text=message,
                        parse_mode="Markdown"
                    )
                    results["success"] += 1
                    results["details"].append({
                        "channel_id": schedule["channel_id"],
                        "status": "success"
                    })
                    
                    # Add delay to avoid rate limits
                    if delay > 0:
                        await asyncio.sleep(delay)
                        
                except Exception as e:
                    results["failed"] += 1
                    results["details"].append({
                        "channel_id": schedule["channel_id"],
                        "status": "failed",
                        "error": str(e)
                    })
                    logger.error(f"Failed to broadcast to {schedule['channel_id']}: {str(e)}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error broadcasting to groups: {str(e)}")
            return {"total": 0, "success": 0, "failed": 0, "details": []}
    
    async def lastperson07_broadcast_to_channels(self, message: str, channel_ids: List[int], delay: float = 1.0) -> Dict[str, Any]:
        """Broadcast message to specific channels."""
        results = {
            "total": len(channel_ids),
            "success": 0,
            "failed": 0,
            "details": []
        }
        
        for channel_id in channel_ids:
            try:
                await self.bot.send_message(
                    chat_id=channel_id,
                    text=message,
                    parse_mode="Markdown"
                )
                results["success"] += 1
                results["details"].append({
                    "channel_id": channel_id,
                    "status": "success"
                })
                
                if delay > 0:
                    await asyncio.sleep(delay)
                    
            except Exception as e:
                results["failed"] += 1
                results["details"].append({
                    "channel_id": channel_id,
                    "status": "failed",
                    "error": str(e)
                })
                logger.error(f"Failed to broadcast to channel {channel_id}: {str(e)}")
        
        return results
    
    async def lastperson07_broadcast_to_users(self, message: str, tier: str = "all", delay: float = 0.5) -> Dict[str, Any]:
        """Broadcast message to users based on tier."""
        try:
            # Get users
            if tier == "all":
                users = await lastperson07_queries.get_all_users()
            else:
                users = await lastperson07_queries.get_all_users(tier=tier)
            
            results = {
                "total": len(users),
                "success": 0,
                "failed": 0,
                "details": []
            }
            
            for user in users:
                try:
                    await self.bot.send_message(
                        chat_id=user["_id"],
                        text=message,
                        parse_mode="Markdown"
                    )
                    results["success"] += 1
                    
                    if delay > 0:
                        await asyncio.sleep(delay)
                        
                except Exception as e:
                    results["failed"] += 1
                    logger.error(f"Failed to broadcast to user {user['_id']}: {str(e)}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error broadcasting to users: {str(e)}")
            return {"total": 0, "success": 0, "failed": 0}
    
    async def lastperson07_broadcast_to_premium_users(self, message: str, delay: float = 0.5) -> Dict[str, Any]:
        """Broadcast message to premium users only."""
        return await self.lastperson07_broadcast_to_users(message, tier="premium", delay=delay)
    
    async def lastperson07_broadcast_to_free_users(self, message: str, delay: float = 0.5) -> Dict[str, Any]:
        """Broadcast message to free users only."""
        return await self.lastperson07_broadcast_to_users(message, tier="free", delay=delay)

# Global broadcaster instance (initialized in app.py)
lastperson07_broadcaster: Optional[LastPerson07Broadcaster] = None

def lastperson07_init_broadcaster(bot: Bot) -> LastPerson07Broadcaster:
    """Initialize broadcaster instance."""
    global lastperson07_broadcaster
    lastperson07_broadcaster = LastPerson07Broadcaster(bot)
    return lastperson07_broadcaster
