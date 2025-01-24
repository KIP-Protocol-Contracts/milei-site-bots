from typing import List
import re
from discord import Message, TextChannel
from config_manager import ConfigManager
from agent_manager import AgentManager
from constants import DISCORD_MAX_MESSAGE_LENGTH

async def send_message_in_chunks(channel: TextChannel, message: str) -> None:
    """Send a message in chunks if it exceeds Discord's message length limit."""
    chunk_size = DISCORD_MAX_MESSAGE_LENGTH
    for i in range(0, len(message), chunk_size):
        chunk = message[i:i + chunk_size]
        await channel.send(chunk)

def is_message_on_channel(message: Message) -> bool:
    """Check if a message is on the monitored channel."""
    config = ConfigManager().get_common_config()
    return message.channel.id == config['kip_test_channel_id']

def is_neighboring_bot_message(message: Message, agent_id: str) -> bool:
    """Check if a message is from a neighboring bot."""
    agent_config = ConfigManager().get_agent_config(agent_id)
    if not agent_config:
        return False
    return message.author.name in agent_config.neighboring_bot_usernames

def is_human_message(message: Message, agent_id: str) -> bool:
    """Check if a message is from a human user."""
    return not (is_neighboring_bot_message(message, agent_id) or 
                is_self_message(message, agent_id))

def is_self_message(message: Message, agent_id: str) -> bool:
    """Check if a message is from the bot itself."""
    agent = AgentManager().get_agent(agent_id)
    return message.author.id == agent['client'].user.id if agent else False

def is_human_message_tags_bot(message: Message, agent_id: str) -> bool:
    """Check if a human message tags or commands the bot."""
    agent = AgentManager().get_agent(agent_id)
    if not agent or not agent['client'].user:
        return False

    return (f"<@{agent['client'].user.id}>" in message.content or
            '!getPrompt' in message.content or
            '!setPrompt' in message.content)

async def bot_has_interacted_too_much(agent_id: str) -> bool:
    """Check if the bot has exceeded its interaction limit."""
    agent = AgentManager().get_agent(agent_id)
    if not agent:
        return False

    async with agent['state'].mutex:
        return agent['state'].context_interaction_count >= 2

def remove_debug_wrap(message: str) -> str:
    """Remove debug code blocks from a message."""
    regex = r'```.*?```'
    return re.sub(regex, '', message, flags=re.DOTALL).strip()

def get_random_delay(min_val: int, max_val: int) -> int:
    """Get a random delay between min and max values."""
    from random import randint
    return randint(min_val, max_val)