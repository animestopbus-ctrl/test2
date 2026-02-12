"""Reactions Module for LastPerson07Bot

This module handles emoji reactions for bot messages and user messages.
"""

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
    """Add a random emoji reaction to a message."""
    try:
        # Check if set_message_reaction is available in this version
        if not hasattr(context.bot, 'set_message_reaction'):
            logger.debug("set_message_reaction not available in this PTB version")
            return False
        
        # Pick random emoji
        random_emoji = random.choice(LASTPERSON07_REACTIONS)
        
        # Try to add reaction - using generic approach since ReactionEmoji might not be available
        try:
            # Try using string directly (newer versions)
            await context.bot.set_message_reaction(
                chat_id=chat_id,
                message_id=message_id,
                reaction=random_emoji
            )
            logger.debug(f"Added reaction {random_emoji} to message {message_id}")
            return True
        except TypeError:
            # Try with list format (older versions)
            await context.bot.set_message_reaction(
                chat_id=chat_id,
                message_id=message_id,
                reaction=[random_emoji]
            )
            logger.debug(f"Added reaction {random_emoji} to message {message_id} (list format)")
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
        # Check if set_message_reaction is available
        if not hasattr(context.bot, 'set_message_reaction'):
            logger.debug("set_message_reaction not available")
            return False
        
        # Pick unique random emojis
        emojis = random.sample(LASTPERSON07_REACTIONS, min(count, len(LASTPERSON07_REACTIONS)))
        
        # Try to add reactions
        try:
            # Try using list format
            await context.bot.set_message_reaction(
                chat_id=chat_id,
                message_id=message_id,
                reaction=emojis
            )
            logger.debug(f"Added {len(emojis)} reactions to message {message_id}")
            return True
        except Exception as e:
            # Try adding one by one
            success_count = 0
            for emoji in emojis:
                try:
                    await context.bot.set_message_reaction(
                        chat_id=chat_id,
                        message_id=message_id,
                        reaction=emoji
                    )
                    success_count += 1
                except:
                    continue
            
            logger.debug(f"Added {success_count}/{len(emojis)} reactions to message {message_id}")
            return success_count > 0
            
    except Exception as e:
        logger.debug(f"Could not add multiple reactions: {str(e)}")
        return False

def lastperson07_get_random_emoji() -> str:
    """Get a random emoji from the reactions pool."""
    return random.choice(LASTPERSON07_REACTIONS)

def lastperson07_get_reaction_emoji_list(count: int = 10) -> list:
    """Get a list of random reaction emojis."""
    return random.sample(LASTPERSON07_REACTIONS, min(count, len(LASTPERSON07_REACTIONS)))
