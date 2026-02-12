"""Fallback reactions.py - no reactions functionality"""

import logging
import random
from typing import Optional
from telegram.ext import ContextTypes

from config.config import LASTPERSON07_REACTIONS

# Setup logging
logger = logging.getLogger(__name__)

async def lastperson07_add_random_reaction(context: ContextTypes.DEFAULT_TYPE,
                                          chat_id: int,
                                          message_id: int) -> bool:
    """Fallback: Add random reaction to a message (disabled for compatibility)."""
    logger.debug("Reactions disabled due to compatibility issues")
    return True  # Always return True to avoid breaking functionality

async def lastperson07_add_reaction_to_user_message(update, 
                                                    context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fallback: Add reaction to user message (disabled)."""
    pass  # Do nothing

async def lastperson07_add_reaction_to_bot_message(context: ContextTypes.DEFAULT_TYPE,
                                                  chat_id: int,
                                                  message_id: int) -> None:
    """Fallback: Add reaction to bot message (disabled)."""
    pass  # Do nothing

async def lastperson07_add_multiple_reactions(context: ContextTypes.DEFAULT_TYPE,
                                             chat_id: int,
                                             message_id: int,
                                             count: int = 3) -> bool:
    """Fallback: Add multiple reactions (disabled)."""
    return True

def lastperson07_get_random_emoji() -> str:
    """Get a random emoji from the reactions pool."""
    return random.choice(LASTPERSON07_REACTIONS)

def lastperson07_get_reaction_emoji_list(count: int = 10) -> list:
    """Get a list of random reaction emojis."""
    return random.sample(LASTPERSON07_REACTIONS, min(count, len(LASTPERSON07_REACTIONS)))
