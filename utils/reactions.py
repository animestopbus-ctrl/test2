"""Reactions Module for LastPerson07Bot

This module handles emoji reactions for bot messages and user messages.
"""

import logging
import random
from typing import Optional
from telegram.ext import ContextTypes

# Fix the import - ReactionTypeEmoji is in telegram.reaction in v20
from telegram.reaction import ReactionEmoji

from config.config import LASTPERSON07_REACTIONS

# Setup logging
logger = logging.getLogger(__name__)

async def lastperson07_add_random_reaction(context: ContextTypes.DEFAULT_TYPE,
                                          chat_id: int,
                                          message_id: int) -> bool:
    """Add a random emoji reaction to a message."""
    try:
        # Pick random emoji
        random_emoji = random.choice(LASTPERSON07_REACTIONS)
        
        # Add reaction - updated for v20
        await context.bot.set_message_reaction(
            chat_id=chat_id,
            message_id=message_id,
            reaction=[ReactionEmoji(random_emoji)]
        )
        
        logger.debug(f"Added reaction {random_emoji} to message {message_id} in chat {chat_id}")
        return True
        
    except Exception as e:
        # Common errors: chat doesn't support reactions, bot doesn't have permission
        logger.debug(f"Could not add reaction to message {message_id}: {str(e)}")
        return False

async def lastperson07_add_reaction_to_user_message(update, 
                                                    context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add random reaction to user's message."""
    try:
        if update.message and update.message.message_id:
            await lastperson07_add_random_reaction(
                context,
                update.effective_chat.id,
                update.message.message_id
            )
    except Exception as e:
        logger.debug(f"Failed to add reaction to user message: {str(e)}")

async def lastperson07_add_reaction_to_bot_message(context: ContextTypes.DEFAULT_TYPE,
                                                  chat_id: int,
                                                  message_id: int) -> None:
    """Add random reaction to bot's own message."""
    try:
        await lastperson07_add_random_reaction(context, chat_id, message_id)
    except Exception as e:
        logger.debug(f"Failed to add reaction to bot message: {str(e)}")

async def lastperson07_add_multiple_reactions(context: ContextTypes.DEFAULT_TYPE,
                                             chat_id: int,
                                             message_id: int,
                                             count: int = 3) -> bool:
    """Add multiple random reactions to a message."""
    try:
        # Pick unique random emojis
        emojis = random.sample(LASTPERSON07_REACTIONS, min(count, len(LASTPERSON07_REACTIONS)))
        
        # Create reaction list - updated for v20
        reactions = [ReactionEmoji(emoji) for emoji in emojis]
        
        # Add reactions
        await context.bot.set_message_reaction(
            chat_id=chat_id,
            message_id=message_id,
            reaction=reactions
        )
        
        logger.debug(f"Added {len(reactions)} reactions to message {message_id}")
        return True
        
    except Exception as e:
        logger.debug(f"Could not add multiple reactions: {str(e)}")
        return False

def lastperson07_get_random_emoji() -> str:
    """Get a random emoji from the reactions pool."""
    return random.choice(LASTPERSON07_REACTIONS)

def lastperson07_get_reaction_emoji_list(count: int = 10) -> list:
    """Get a list of random reaction emojis."""
    return random.sample(LASTPERSON07_REACTIONS, min(count, len(LASTPERSON07_REACTIONS)))
