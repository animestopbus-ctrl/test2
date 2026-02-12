"""Wallpaper Fetcher for LastPerson07Bot

This module handles fetching wallpapers from multiple APIs with fallback,
image validation, and temporary file management using Pillow.
"""

import os
import logging
import asyncio
import aiohttp
from PIL import Image
from typing import Optional, Tuple, Dict, Any
from datetime import datetime
import tempfile
import re

from config.config import (
    LASTPERSON07_API_ENDPOINTS, LASTPERSON07_MIN_IMAGE_WIDTH,
    LASTPERSON07_MIN_IMAGE_HEIGHT, LASTPERSON07_DEFAULT_CATEGORY,
    LASTPERSON07_UNSPLASH_KEY, LASTPERSON07_PEXELS_KEY,
    LASTPERSON07_PIXABAY_KEY, LASTPERSON07_MAX_FILE_SIZE_MB
)
from db.models import LastPerson07WallpaperData

# Setup logging
logger = logging.getLogger(__name__)

class LastPerson07WallpaperFetcher:
    """Handles wallpaper fetching from multiple APIs with fallback."""
    
    def __init__(self):
        """Initialize the fetcher with API keys."""
        self.api_keys = {
            "unsplash": LASTPERSON07_UNSPLASH_KEY,
            "pexels": LASTPERSON07_PEXELS_KEY,
            "pixabay": LASTPERSON07_PIXABAY_KEY
        }
        self.pillow_available = self._check_pillow()
    
    def _check_pillow(self) -> bool:
        """Check if Pillow is available and working."""
        try:
            # Test basic Pillow functionality
            test_img = Image.new('RGB', (100, 100), color='red')
            return True
        except Exception as e:
            logger.error(f"Pillow not available: {str(e)}. Image validation will be skipped.")
            return False
    
    async def fetch_wallpaper(self, category: str = LASTPERSON07_DEFAULT_CATEGORY) -> Optional[LastPerson07WallpaperData]:
        """Fetch wallpaper using API fallback chain."""
        sanitized_category = self.lastperson07_sanitize_category(category)
        
        # Try APIs in order: Unsplash -> Pexels -> Pixabay
        for api_source in ["unsplash", "pexels", "pixabay"]:
            try:
                logger.info(f"Attempting to fetch from {api_source} API")
                wallpaper_data = await self.lastperson07_fetch_from_api(api_source, sanitized_category)
                
                if wallpaper_data:
                    # Download and validate image (skip validation if Pillow not available)
                    if not self.pillow_available or await self.lastperson07_download_and_validate_image(wallpaper_data.image_url):
                        logger.info(f"Successfully fetched wallpaper from {api_source}")
                        return wallpaper_data
                    else:
                        logger.warning(f"Image validation failed for {api_source}")
                        continue
                        
            except Exception as e:
                logger.error(f"Error fetching from {api_source}: {str(e)}")
                continue
        
        logger.error("All APIs failed to provide a valid wallpaper")
        return None
    
    async def lastperson07_fetch_from_api(self, api_source: str, category: str) -> Optional[LastPerson07WallpaperData]:
        """Fetch wallpaper data from specific API source."""
        if api_source == "unsplash":
            return await self.lastperson07_fetch_from_unsplash(category)
        elif api_source == "pexels":
            return await self.lastperson07_fetch_from_pexels(category)
        elif api_source == "pixabay":
            return await self.lastperson07_fetch_from_pixabay(category)
        else:
            logger.error(f"Unknown API source: {api_source}")
            return None
    
    async def lastperson07_fetch_from_unsplash(self, category: str) -> Optional[LastPerson07WallpaperData]:
        """Fetch wallpaper from Unsplash API."""
        if not self.api_keys["unsplash"]:
            logger.error("Unsplash API key not configured")
            return None
        
        url = LASTPERSON07_API_ENDPOINTS["unsplash"]
        params = {
            "client_id": self.api_keys["unsplash"],
            "query": category,
            "orientation": "landscape",
            "content_filter": "high",
            "per_page": 1
        }
        
        headers = {
            "Accept-Version": "v1",
            "User-Agent": "LastPerson07Bot/1.0"
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and len(data) > 0:
                            photo = data[0]
                            
                            return LastPerson07WallpaperData(
                                title=photo.get("alt_description", "Untitled"),
                                width=photo.get("width", 0),
                                height=photo.get("height", 0),
                                author=photo.get("user", {}).get("name", "Unknown"),
                                source="Unsplash",
                                image_url=photo.get("urls", {}).get("regular", ""),
                                download_url=photo.get("urls", {}).get("full", "")
                            )
                    elif response.status == 403:
                        logger.warning("Unsplash API rate limit exceeded")
                    else:
                        logger.error(f"Unsplash API error: {response.status}")
                        
            except Exception as e:
                logger.error(f"Error fetching from Unsplash: {str(e)}")
        
        return None
    
    async def lastperson07_fetch_from_pexels(self, category: str) -> Optional[LastPerson07WallpaperData]:
        """Fetch wallpaper from Pexels API."""
        if not self.api_keys["pexels"]:
            logger.error("Pexels API key not configured")
            return None
        
        url = LASTPERSON07_API_ENDPOINTS["pexels"]
        params = {
            "query": category,
            "per_page": 1,
            "page": 1
        }
        
        headers = {
            "Authorization": self.api_keys["pexels"],
            "User-Agent": "LastPerson07Bot/1.0"
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        photos = data.get("photos", [])
                        
                        if photos:
                            photo = photos[0]
                            
                            return LastPerson07WallpaperData(
                                title=photo.get("alt", "Untitled"),
                                width=photo.get("width", 0),
                                height=photo.get("height", 0),
                                author=photo.get("photographer", "Unknown"),
                                source="Pexels",
                                image_url=photo.get("src", {}).get("large", ""),
                                download_url=photo.get("src", {}).get("original", "")
                            )
                    elif response.status == 429:
                        logger.warning("Pexels API rate limit exceeded")
                    else:
                        logger.error(f"Pexels API error: {response.status}")
                        
            except Exception as e:
                logger.error(f"Error fetching from Pexels: {str(e)}")
        
        return None
    
    async def lastperson07_fetch_from_pixabay(self, category: str) -> Optional[LastPerson07WallpaperData]:
        """Fetch wallpaper from Pixabay API."""
        if not self.api_keys["pixabay"]:
            logger.error("Pixabay API key not configured")
            return None
        
        url = LASTPERSON07_API_ENDPOINTS["pixabay"]
        params = {
            "key": self.api_keys["pixabay"],
            "q": category,
            "image_type": "photo",
            "orientation": "horizontal",
            "safesearch": "true",
            "min_width": str(LASTPERSON07_MIN_IMAGE_WIDTH),
            "min_height": str(LASTPERSON07_MIN_IMAGE_HEIGHT),
            "order": "popular",
            "per_page": 3
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        hits = data.get("hits", [])
                        
                        # Find first suitable image
                        for hit in hits:
                            if hit.get("imageWidth", 0) >= LASTPERSON07_MIN_IMAGE_WIDTH and \
                               hit.get("imageHeight", 0) >= LASTPERSON07_MIN_IMAGE_HEIGHT:
                                
                                return LastPerson07WallpaperData(
                                    title=hit.get("tags", "Untitled").split(",")[0],
                                    width=hit.get("imageWidth", 0),
                                    height=hit.get("imageHeight", 0),
                                    author=hit.get("user", "Unknown"),
                                    source="Pixabay",
                                    image_url=hit.get("webformatURL", ""),
                                    download_url=hit.get("largeImageURL", "")
                                )
                    elif response.status == 429:
                        logger.warning("Pixabay API rate limit exceeded")
                    else:
                        logger.error(f"Pixabay API error: {response.status}")
                        
            except Exception as e:
                logger.error(f"Error fetching from Pixabay: {str(e)}")
        
        return None
    
    async def lastperson07_download_and_validate_image(self, image_url: str) -> bool:
        """Download image and validate resolution using Pillow."""
        # Skip validation if Pillow not available
        if not self.pillow_available:
            logger.info("Skipping image validation (Pillow not available)")
            return True
        
        temp_file = None
        
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            temp_path = temp_file.name
            temp_file.close()
            
            # Download image
            timeout = aiohttp.ClientTimeout(total=60)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(image_url) as response:
                    if response.status == 200:
                        # Check content size
                        content_length = response.headers.get('content-length')
                        if content_length and int(content_length) > LASTPERSON07_MAX_FILE_SIZE_MB * 1024 * 1024:
                            logger.warning(f"Image too large: {content_length} bytes")
                            if os.path.exists(temp_path):
                                os.unlink(temp_path)
                            return False
                        
                        # Download the image
                        with open(temp_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(1024):
                                f.write(chunk)
                    else:
                        logger.error(f"Failed to download image: HTTP {response.status}")
                        if os.path.exists(temp_path):
                            os.unlink(temp_path)
                        return False
            
            # Validate image with Pillow
            try:
                with Image.open(temp_path) as img:
                    width, height = img.size
                    
                    # Check minimum resolution
                    if width < LASTPERSON07_MIN_IMAGE_WIDTH or height < LASTPERSON07_MIN_IMAGE_HEIGHT:
                        logger.warning(f"Image resolution too small: {width}x{height}")
                        if os.path.exists(temp_path):
                            os.unlink(temp_path)
                        return False
                    
                    # Verify image format
                    if img.format not in ['JPEG', 'JPG', 'PNG', 'WEBP']:
                        logger.warning(f"Unsupported image format: {img.format}")
                        if os.path.exists(temp_path):
                            os.unlink(temp_path)
                        return False
                    
                    logger.info(f"Image validated successfully: {width}x{height} ({img.format})")
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                    return True
                    
            except Exception as e:
                logger.error(f"Failed to validate image with Pillow: {str(e)}")
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                return False
            
        except Exception as e:
            logger.error(f"Error validating image: {str(e)}")
            if temp_file and os.path.exists(temp_path.name):
                os.unlink(temp_file.name)
            return False
    
    def lastperson07_sanitize_category(self, category: str) -> str:
        """Sanitize category input."""
        if not category:
            return LASTPERSON07_DEFAULT_CATEGORY
        
        # Remove special characters and limit length
        sanitized = re.sub(r'[^a-zA-Z0-9\s]', '', category)
        sanitized = ' '.join(sanitized.split())  # Remove extra spaces
        
        # Limit to 50 characters
        if len(sanitized) > 50:
            sanitized = sanitized[:50].rstrip()
        
        # If empty after sanitization, use default
        if not sanitized:
            return LASTPERSON07_DEFAULT_CATEGORY
        
        return sanitized.lower()

# Global fetcher instance
lastperson07_wallpaper_fetcher = LastPerson07WallpaperFetcher()
