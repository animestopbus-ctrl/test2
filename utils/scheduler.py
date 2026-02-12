"""Scheduler Module for LastPerson07Bot

This module handles job scheduling for automated wallpaper posting.
"""

import logging
import asyncio
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from telegram import Bot
from telegram.ext import Application

from config.config import LASTPERSON07_DEFAULT_CATEGORY
from db.queries import lastperson07_queries
from utils.fetcher import lastperson07_wallpaper_fetcher
from utils.promoter import lastperson07_add_promo_button_if_free
from utils.metadata import lastperson07_format_wallpaper_caption
from utils.reactions import lastperson07_add_random_reaction

# Setup logging
logger = logging.getLogger(__name__)

class LastPerson07Scheduler:
    """Job scheduler for automated wallpaper posting."""
    
    def __init__(self, application: Application):
        """Initialize scheduler."""
        self.application = application
        self.scheduler = AsyncIOScheduler()
        self.running = False
    
    async def start(self):
        """Start the scheduler."""
        if not self.running:
            self.scheduler.start()
            self.running = True
            logger.info("Scheduler started")
            
            # Load existing schedules
            await self.lastperson07_load_schedules()
    
    async def stop(self):
        """Stop the scheduler."""
        if self.running:
            self.scheduler.shutdown(wait=True)
            self.running = False
            logger.info("Scheduler stopped")
    
    async def lastperson07_load_schedules(self):
        """Load schedules from database and create jobs."""
        schedules = await lastperson07_queries.get_schedules(active_only=True)
        
        for schedule_data in schedules:
            try:
                channel_id = schedule_data["channel_id"]
                interval = schedule_data["interval"]
                category = schedule_data.get("category", LASTPERSON07_DEFAULT_CATEGORY)
                
                # Create trigger based on interval
                if interval == "hourly":
                    trigger = IntervalTrigger(hours=1)
                elif interval == "daily":
                    trigger = IntervalTrigger(days=1)
                else:
                    logger.warning(f"Unknown interval: {interval}")
                    continue
                
                # Add job
                job_id = f"schedule_{channel_id}_{interval}"
                self.scheduler.add_job(
                    func=self.lastperson07_post_wallpaper_job,
                    trigger=trigger,
                    args=[channel_id, category],
                    id=job_id,
                    name=f"Wallpaper posting for {channel_id}",
                    replace_existing=True
                )
                
                logger.info(f"Added scheduled job: {job_id}")
                
            except Exception as e:
                logger.error(f"Error loading schedule {schedule_data}: {str(e)}")
    
    async def lastperson07_add_schedule(self, channel_id: int, interval: str, category: str):
        """Add a new schedule."""
        try:
            # Create schedule in database
            await lastperson07_queries.create_schedule(channel_id, interval, category)
            
            # Create trigger
            if interval == "hourly":
                trigger = IntervalTrigger(hours=1)
            elif interval == "daily":
                trigger = IntervalTrigger(days=1)
            else:
                logger.error(f"Invalid interval: {interval}")
                return False
            
            # Add job
            job_id = f"schedule_{channel_id}_{interval}"
            self.scheduler.add_job(
                func=self.lastperson07_post_wallpaper_job,
                trigger=trigger,
                args=[channel_id, category],
                id=job_id,
                name=f"Wallpaper posting for {channel_id}",
                replace_existing=True
            )
            
            logger.info(f"Added new schedule: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding schedule: {str(e)}")
            return False
    
    async def lastperson07_remove_schedule(self, channel_id: int, interval: str):
        """Remove a schedule."""
        try:
            # Remove job from scheduler
            job_id = f"schedule_{channel_id}_{interval}"
            try:
                self.scheduler.remove_job(job_id)
            except:
                pass  # Job might not exist
            
            # Mark as inactive in database
            await lastperson07_queries.update_schedule_last_post(channel_id)
            
            logger.info(f"Removed schedule: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing schedule: {str(e)}")
            return False
    
    async def lastperson07_post_wallpaper_job(self, channel_id: int, category: str):
        """Job function to post wallpaper to channel/group."""
        try:
            # Fetch wallpaper
            wallpaper_data = await lastperson07_wallpaper_fetcher.fetch_wallpaper(category)
            
            if not wallpaper_data:
                logger.error(f"Failed to fetch wallpaper for scheduled post to {channel_id}")
                return
            
            # Format caption
            caption = lastperson07_format_wallpaper_caption(wallpaper_data)
            
            # Create keyboard (no promo for scheduled posts)
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            
            # Add download button
            keyboard = []
            
            if wallpaper_data.download_url:
                keyboard.append([InlineKeyboardButton("⬇️ Download", url=wallpaper_data.download_url)])
            
            reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
            
            # Send to channel
            sent_message = await self.application.bot.send_photo(
                chat_id=channel_id,
                photo=wallpaper_data.image_url,
                caption=caption,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            
            # Add reaction
            await lastperson07_add_random_reaction(
                self.application,
                channel_id,
                sent_message.message_id
            )
            
            # Update schedule
            await lastperson07_queries.update_schedule_last_post(channel_id)
            
            logger.info(f"Posted scheduled wallpaper to {channel_id}")
            
        except Exception as e:
            logger.error(f"Error in scheduled wallpaper posting: {str(e)}")
    
    async def lastperson07_get_job_list(self) -> list:
        """Get list of all scheduled jobs."""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time
            })
        return jobs

# Global scheduler instance
lastperson07_scheduler: Optional[LastPerson07Scheduler] = None

async def lastperson07_init_scheduler(application: Application) -> LastPerson07Scheduler:
    """Initialize scheduler instance."""
    global lastperson07_scheduler
    lastperson07_scheduler = LastPerson07Scheduler(application)
    await lastperson07_scheduler.start()
    return lastperson07_scheduler
