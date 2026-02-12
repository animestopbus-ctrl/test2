import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from config.config import LASTPERSON07_FREE_FETCH_LIMIT
from db.client import lastperson07_db_client
from db.models import (
    LastPerson07User, LastPerson07Schedule, LastPerson07ApiUrl,
    LastPerson07BotSettings, UserTier, ScheduleInterval
)

# Setup logging
logger = logging.getLogger(__name__)

class LastPerson07Queries:
    """Database query operations wrapper."""
    
    def __init__(self):
        """Initialize queries wrapper with database client."""
        self.db = lastperson07_db_client
    
    async def get_user(self, user_id: int) -> Optional[LastPerson07User]:
        """Get user by Telegram ID."""
        try:
            user_data = await self.db.find_one("users", {"_id": user_id})
            if user_data:
                return LastPerson07User.from_dict(user_data)
            return None
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {str(e)}")
            return None
    
    async def create_user(self, user_id: int, username: str, 
                         first_name: str) -> bool:
        """Create a new user in database."""
        try:
            now = datetime.now(timezone.utc)
            user = LastPerson07User(
                _id=user_id,
                username=username,
                first_name=first_name,
                join_date=now
            )
            
            result = await self.db.insert_one("users", user.to_dict())
            return result is not None
        except Exception as e:
            logger.error(f"Error creating user {user_id}: {str(e)}")
            return False
    
    async def update_user_fetch_count(self, user_id: int) -> bool:
        """Increment user's fetch count and update last fetch date."""
        try:
            now = datetime.now(timezone.utc)
            update = {
                "$inc": {"fetch_count": 1},
                "$set": {"last_fetch_date": now}
            }
            
            result = await self.db.update_one("users", {"_id": user_id}, update)
            return result
        except Exception as e:
            logger.error(f"Error updating fetch count for user {user_id}: {str(e)}")
            return False
    
    async def check_daily_limit(self, user_id: int) -> tuple[bool, int]:
        """Check if user has reached daily fetch limit."""
        try:
            user = await self.get_user(user_id)
            if not user:
                return False, LASTPERSON07_FREE_FETCH_LIMIT
            
            if user.tier == UserTier.PREMIUM:
                return False, -1  # Unlimited for premium
            
            today = datetime.now(timezone.utc).date()
            last_fetch = user.last_fetch_date
            
            # Check if last fetch was today
            if last_fetch and last_fetch.date() == today:
                remaining = max(0, LASTPERSON07_FREE_FETCH_LIMIT - user.fetch_count)
                return remaining == 0, remaining
            else:
                # New day, reset count
                await self.db.update_one(
                    "users",
                    {"_id": user_id},
                    {"$set": {"fetch_count": 0}}
                )
                return False, LASTPERSON07_FREE_FETCH_LIMIT
                
        except Exception as e:
            logger.error(f"Error checking daily limit for user {user_id}: {str(e)}")
            return False, 0
    
    async def upgrade_to_premium(self, user_id: int, 
                                expiration: Optional[datetime] = None) -> bool:
        """Upgrade user to premium tier."""
        try:
            update = {
                "$set": {
                    "tier": UserTier.PREMIUM.value,
                    "expiration": expiration
                }
            }
            
            result = await self.db.update_one("users", {"_id": user_id}, update)
            
            if result:
                logger.info(f"User {user_id} upgraded to premium")
            return result
        except Exception as e:
            logger.error(f"Error upgrading user {user_id} to premium: {str(e)}")
            return False
    
    async def downgrade_to_free(self, user_id: int) -> bool:
        """Downgrade user to free tier."""
        try:
            update = {
                "$set": {
                    "tier": UserTier.FREE.value,
                    "expiration": None
                }
            }
            
            result = await self.db.update_one("users", {"_id": user_id}, update)
            
            if result:
                logger.info(f"User {user_id} downgraded to free")
            return result
        except Exception as e:
            logger.error(f"Error downgrading user {user_id} to free: {str(e)}")
            return False
    
    async def ban_user(self, user_id: int) -> bool:
        """Ban a user."""
        try:
            result = await self.db.update_one(
                "users",
                {"_id": user_id},
                {"$set": {"banned": True}}
            )
            
            if result:
                logger.info(f"User {user_id} has been banned")
            return result
        except Exception as e:
            logger.error(f"Error banning user {user_id}: {str(e)}")
            return False
    
    async def unban_user(self, user_id: int) -> bool:
        """Unban a user."""
        try:
            result = await self.db.update_one(
                "users",
                {"_id": user_id},
                {"$set": {"banned": False}}
            )
            
            if result:
                logger.info(f"User {user_id} has been unbanned")
            return result
        except Exception as e:
            logger.error(f"Error unbanning user {user_id}: {str(e)}")
            return False
    
    async def get_all_users(self, tier: Optional[str] = None, 
                           banned: Optional[bool] = None) -> List[Dict[str, Any]]:
        """Get all users with optional filters."""
        try:
            query = {}
            
            if tier:
                query["tier"] = tier
            if banned is not None:
                query["banned"] = banned
            
            users = await self.db.find_many("users", query, limit=1000)
            return users
        except Exception as e:
            logger.error(f"Error getting all users: {str(e)}")
            return []
    
    async def create_schedule(self, channel_id: int, interval: str, 
                            category: str) -> bool:
        """Create a new schedule."""
        try:
            schedule = LastPerson07Schedule(
                _id=None,
                channel_id=channel_id,
                interval=ScheduleInterval(interval),
                category=category
            )
            
            result = await self.db.insert_one("schedules", schedule.to_dict())
            return result is not None
        except Exception as e:
            logger.error(f"Error creating schedule: {str(e)}")
            return False
    
    async def get_schedules(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all schedules."""
        try:
            query = {}
            if active_only:
                query["active"] = True
            
            schedules = await self.db.find_many("schedules", query, limit=100)
            return schedules
        except Exception as e:
            logger.error(f"Error getting schedules: {str(e)}")
            return []
    
    async def update_schedule_last_post(self, channel_id: int) -> bool:
        """Update schedule's last post time."""
        try:
            now = datetime.now(timezone.utc)
            result = await self.db.update_one(
                "schedules",
                {"channel_id": channel_id},
                {"$set": {"last_post_time": now}}
            )
            return result
        except Exception as e:
            logger.error(f"Error updating schedule last post: {str(e)}")
            return False
    
    async def get_bot_settings(self) -> LastPerson07BotSettings:
        """Get global bot settings."""
        try:
            settings_data = await self.db.find_one("bot_settings", {"_id": "settings"})
            
            if settings_data:
                return LastPerson07BotSettings.from_dict(settings_data)
            else:
                # Create default settings
                default_settings = LastPerson07BotSettings()
                await self.db.insert_one("bot_settings", default_settings.to_dict())
                return default_settings
        except Exception as e:
            logger.error(f"Error getting bot settings: {str(e)}")
            return LastPerson07BotSettings()
    
    async def update_bot_settings(self, settings: Dict[str, Any]) -> bool:
        """Update global bot settings."""
        try:
            result = await self.db.update_one(
                "bot_settings",
                {"_id": "settings"},
                {"$set": settings},
                upsert=True
            )
            return result
        except Exception as e:
            logger.error(f"Error updating bot settings: {str(e)}")
            return False
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive bot statistics."""
        try:
            stats = {
                "total_users": await self.db.count_documents("users", {}),
                "premium_users": await self.db.count_documents("users", {"tier": "premium"}),
                "free_users": await self.db.count_documents("users", {"tier": "free"}),
                "banned_users": await self.db.count_documents("users", {"banned": True}),
                "active_schedules": await self.db.count_documents("schedules", {"active": True}),
            }
            
            # Calculate total fetches
            pipeline = [
                {"$group": {"_id": None, "total_fetches": {"$sum": "$fetch_count"}}}
            ]
            results = await self.db.aggregate("users", pipeline)
            if results:
                stats["total_fetches"] = results[0].get("total_fetches", 0)
            else:
                stats["total_fetches"] = 0
            
            return stats
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {}

# Global queries instance
lastperson07_queries = LastPerson07Queries()

