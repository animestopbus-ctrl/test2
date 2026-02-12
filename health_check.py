"""health_check.py - Simple health check for Render"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def health_check():
    """Perform health check."""
    try:
        # Check required environment variables
        telegram_token = os.getenv("TELEGRAM_TOKEN")
        if not telegram_token:
            print("❌ TELEGRAM_TOKEN not set")
            return False
        
        # Check if we can import main modules
        try:
            from app import lastperson07_bot
        except ImportError as e:
            print(f"❌ Failed to import app: {e}")
            return False
        
        # Check if bot is running
        if hasattr(lastperson07_bot, 'running') and lastperson07_bot.running:
            print("✅ Bot is running")
            return True
        else:
            print("❌ Bot is not running")
            return False
            
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(health_check())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"Health check error: {str(e)}")
        sys.exit(1)
