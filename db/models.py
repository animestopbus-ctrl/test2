"""Data Models for LastPerson07Bot

This module defines data models and schemas used throughout the application.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

class UserTier(Enum):
    """User subscription tiers."""
    FREE = "free"
    PREMIUM = "premium"

class ScheduleInterval(Enum):
    """Schedule intervals for automated posting."""
    HOURLY = "hourly"
    DAILY = "daily"

@dataclass
class LastPerson07User:
    """User model for database storage."""
    _id: int  # Telegram user ID
    username: Optional[str]
    first_name: str
    tier: UserTier = UserTier.FREE
    fetch_count: int = 0
    last_fetch_date: Optional[datetime] = None
    join_date: datetime = None
    banned: bool = False
    expiration: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB storage."""
        return {
            "_id": self._id,
            "username": self.username,
            "first_name": self.first_name,
            "tier": self.tier.value,
            "fetch_count": self.fetch_count,
            "last_fetch_date": self.last_fetch_date,
            "join_date": self.join_date,
            "banned": self.banned,
            "expiration": self.expiration
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LastPerson07User":
        """Create instance from dictionary."""
        return cls(
            _id=data["_id"],
            username=data.get("username"),
            first_name=data["first_name"],
            tier=UserTier(data.get("tier", "free")),
            fetch_count=data.get("fetch_count", 0),
            last_fetch_date=data.get("last_fetch_date"),
            join_date=data.get("join_date", datetime.now()),
            banned=data.get("banned", False),
            expiration=data.get("expiration")
        )

@dataclass
class LastPerson07Schedule:
    """Schedule model for automated wallpaper posting."""
    _id: Optional[str]
    channel_id: int
    interval: ScheduleInterval
    category: str
    last_post_time: Optional[datetime] = None
    active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB storage."""
        return {
            "_id": self._id,
            "channel_id": self.channel_id,
            "interval": self.interval.value,
            "category": self.category,
            "last_post_time": self.last_post_time,
            "active": self.active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LastPerson07Schedule":
        """Create instance from dictionary."""
        return cls(
            _id=data.get("_id"),
            channel_id=data["channel_id"],
            interval=ScheduleInterval(data["interval"]),
            category=data["category"],
            last_post_time=data.get("last_post_time"),
            active=data.get("active", True)
        )

@dataclass
class LastPerson07ApiUrl:
    """Additional API URL configuration."""
    _id: Optional[str]
    url: str
    source_name: str
    api_key: Optional[str] = None
    active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB storage."""
        return {
            "_id": self._id,
            "url": self.url,
            "source_name": self.source_name,
            "api_key": self.api_key,
            "active": self.active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LastPerson07ApiUrl":
        """Create instance from dictionary."""
        return cls(
            _id=data.get("_id"),
            url=data["url"],
            source_name=data["source_name"],
            api_key=data.get("api_key"),
            active=data.get("active", True)
        )

@dataclass
class LastPerson07BotSettings:
    """Global bot settings."""
    _id: str = "settings"
    maintenance: bool = False
    bin_channel_id: Optional[int] = None
    delay_minutes: int = 5
    owners: List[int] = None
    
    def __post_init__(self):
        if self.owners is None:
            self.owners = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB storage."""
        return {
            "_id": self._id,
            "maintenance": self.maintenance,
            "bin_channel_id": self.bin_channel_id,
            "delay_minutes": self.delay_minutes,
            "owners": self.owners
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LastPerson07BotSettings":
        """Create instance from dictionary."""
        return cls(
            _id=data.get("_id", "settings"),
            maintenance=data.get("maintenance", False),
            bin_channel_id=data.get("bin_channel_id"),
            delay_minutes=data.get("delay_minutes", 5),
            owners=data.get("owners", [])
        )

@dataclass
class LastPerson07WallpaperData:
    """Wallpaper data structure from API responses."""
    title: str
    width: int
    height: int
    author: str
    source: str
    image_url: str
    download_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "width": self.width,
            "height": self.height,
            "author": self.author,
            "source": self.source,
            "image_url": self.image_url,
            "download_url": self.download_url
        }
