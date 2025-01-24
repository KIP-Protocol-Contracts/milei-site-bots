from typing import Dict
from enum import Enum
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN_LENGTH_VARIABLES: Dict[int, str] = {
    20: "one- or two-word",
    40: "one-sentence",
    200: "one-paragraph"
}

EOS_TOKEN_MAP: Dict[str, str] = {
    'mistral': '</end>',
    'openai': '__',
    'anthropic': '__',
    'deepseek': '</end>'
}

DEFAULT_BOT_USERNAMES: Dict[int, str] = {
    1: 'stefani_tan',
    2: 'michaelwilliams309015',
    3: 'ianwright1579'
}

MESSAGE_HISTORY_MINUTES = 10
MAX_CONTEXT_INTERACTIONS = 2
TYPING_SPEED_MS = 200  # ms per character
DISCORD_MAX_MESSAGE_LENGTH = 2000