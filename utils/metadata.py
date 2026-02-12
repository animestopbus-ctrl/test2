"""Metadata Module for LastPerson07Bot

This module handles caption formatting and metadata processing.
"""

import logging
from typing import Optional
from db.models import LastPerson07WallpaperData

# Setup logging
logger = logging.getLogger(__name__)

def lastperson07_format_wallpaper_caption(wallpaper_data: LastPerson07WallpaperData) -> str:
    """Format wallpaper caption in the required style."""
    try:
        # Format: "Beautiful Sunset Beach | 3840×2160 | Photo by Alex Smith on Unsplash\nDownload: [link]"
        
        # Clean title
        title = wallpaper_data.title or "Untitled"
        if len(title) > 50:
            title = title[:47] + "..."
        
        # Format resolution
        resolution = f"{wallpaper_data.width}×{wallpaper_data.height}"
        
        # Format author line
        author_line = f"Photo by {wallpaper_data.author} on {wallpaper_data.source}"
        
        # Format download line
        download_line = f"Download: {wallpaper_data.download_url}" if wallpaper_data.download_url else ""
        
        # Combine
        caption = f"{title} | {resolution} | {author_line}\n{download_line}"
        
        return caption
        
    except Exception as e:
        logger.error(f"Error formatting caption: {str(e)}")
        return "Wallpaper"

def lastperson07_extract_metadata_from_unsplash(photo_data: dict) -> Optional[LastPerson07WallpaperData]:
    """Extract metadata from Unsplash API response."""
    try:
        return LastPerson07WallpaperData(
            title=photo_data.get("alt_description", "Untitled"),
            width=photo_data.get("width", 0),
            height=photo_data.get("height", 0),
            author=photo_data.get("user", {}).get("name", "Unknown"),
            source="Unsplash",
            image_url=photo_data.get("urls", {}).get("regular", ""),
            download_url=photo_data.get("urls", {}).get("full", "")
        )
    except Exception as e:
        logger.error(f"Error extracting Unsplash metadata: {str(e)}")
        return None

def lastperson07_extract_metadata_from_pexels(photo_data: dict) -> Optional[LastPerson07WallpaperData]:
    """Extract metadata from Pexels API response."""
    try:
        return LastPerson07WallpaperData(
            title=photo_data.get("alt", "Untitled"),
            width=photo_data.get("width", 0),
            height=photo_data.get("height", 0),
            author=photo_data.get("photographer", "Unknown"),
            source="Pexels",
            image_url=photo_data.get("src", {}).get("large", ""),
            download_url=photo_data.get("src", {}).get("original", "")
        )
    except Exception as e:
        logger.error(f"Error extracting Pexels metadata: {str(e)}")
        return None

def lastperson07_extract_metadata_from_pixabay(photo_data: dict) -> Optional[LastPerson07WallpaperData]:
    """Extract metadata from Pixabay API response."""
    try:
        tags = photo_data.get("tags", "Untitled").split(",")[0]
        return LastPerson07WallpaperData(
            title=tags.strip() if tags else "Untitled",
            width=photo_data.get("imageWidth", 0),
            height=photo_data.get("imageHeight", 0),
            author=photo_data.get("user", "Unknown"),
            source="Pixabay",
            image_url=photo_data.get("webformatURL", ""),
            download_url=photo_data.get("largeImageURL", "")
        )
    except Exception as e:
        logger.error(f"Error extracting Pixabay metadata: {str(e)}")
        return None

def lastperson07_validate_image_metadata(wallpaper_data: LastPerson07WallpaperData) -> bool:
    """Validate wallpaper metadata meets requirements."""
    try:
        # Check required fields
        if not all([
            wallpaper_data.title,
            wallpaper_data.author,
            wallpaper_data.source,
            wallpaper_data.image_url
        ]):
            logger.warning("Missing required metadata fields")
            return False
        
        # Check resolution
        if (wallpaper_data.width < 1920 or 
            wallpaper_data.height < 1080):
            logger.warning(f"Image too small: {wallpaper_data.width}x{wallpaper_data.height}")
            return False
        
        # Check URL format
        if not wallpaper_data.image_url.startswith(('http://', 'https://')):
            logger.warning("Invalid image URL format")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating metadata: {str(e)}")
        return False
