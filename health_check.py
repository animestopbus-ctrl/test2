"""health_check.py - Simple health check for Render"""

import asyncio
import sys
from app import lastperson07_bot

async def health_check():
    """Perform health check."""
    try:
        # Check if bot is running
        if lastperson07_bot and lastperson07_bot.running:
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
