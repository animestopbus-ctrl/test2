# render_start.py - Render-specific startup
import os
import logging
import asyncio

async def render_startup():
    """Render-specific startup configuration."""
    # Set Render-specific configurations
    if os.getenv("RENDER") == "true":
        # Render-specific settings
        logging.info("Running on Render platform")
        
        # Ensure webhooks work on Render
        os.environ["WEBHOOK_MODE"] = "true"
        os.environ["PORT"] = os.getenv("PORT", "8080")
        
        # Try to get webhook URL
        webhook_url = os.getenv("WEBHOOK_URL")
        if webhook_url:
            logging.info(f"Webhook URL: {webhook_url}")
    
    return True

if __name__ == "__main__":
    asyncio.run(render_startup())
