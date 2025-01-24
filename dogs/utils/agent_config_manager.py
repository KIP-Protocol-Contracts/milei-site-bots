from typing import Dict, List, Optional, TypedDict, Union
from dataclasses import dataclass
import os
from dotenv import load_dotenv
from enum import Enum

class AIAgents(str, Enum):
    MISTRAL = 'mistral'
    OPENAI = 'openai'
    ANTHROPIC = 'anthropic'
    DEEPSEEK = 'deepseek'

@dataclass
class ChatConfig:
    template: str
    prompt: str
    tone_variable: str
    eos_token: str
    token_length_array: List[int]
    username: str

@dataclass
class AgentConfig:
    id: str
    api_endpoint: AIAgents
    api_key: str
    discord_token: str
    message_delay_min: int
    message_delay_max: int
    neighboring_bot_usernames: List[str]
    chat_config: ChatConfig

class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            load_dotenv()
            self.configs: Dict[str, AgentConfig] = {}
            self._load_configs()
            self._initialized = True

    @staticmethod
    def load_api_key(ai_agent: AIAgents) -> str:
        key_map = {
            AIAgents.MISTRAL: 'MISTRAL_KEY',
            AIAgents.OPENAI: 'AL_OPENAI_KEY',
            AIAgents.ANTHROPIC: 'ANTHROPIC_KEY',
            AIAgents.DEEPSEEK: 'DEEPSEEK_KEY'
        }
        env_key = key_map.get(ai_agent)
        if not env_key:
            raise ValueError(f"Unsupported AI agent: {ai_agent}")
        return os.getenv(env_key, '')

    def _load_configs(self):
        template = os.getenv('CHAT_TEMPLATE', 
                           "{Prompt}\n\n{ChannelContext}\n\n{SelectedMessage}\n\nYou: ")
        
        bots_number = int(os.getenv('BOTS_NUMBER', '0'))
        
        for i in range(1, bots_number + 1):
            ai_agent = os.getenv(f'AI_AGENTS_BOT_{i}')
            if not ai_agent:
                continue

            api_key = self.load_api_key(AIAgents(ai_agent))
            
            self.configs[f'ai-agent-{i}'] = AgentConfig(
                id=ai_agent,
                api_endpoint=AIAgents(ai_agent),
                api_key=api_key,
                discord_token=os.getenv(f'DISCORD_TOKEN_BOT_{i}', ''),
                message_delay_min=(i-1)*2000,
                message_delay_max=i*2000,
                neighboring_bot_usernames=os.getenv(
                    f'NEIGHBORING_BOT_USERNAMES_BOT_{i}', ''
                ).split(',') if os.getenv(f'NEIGHBORING_BOT_USERNAMES_BOT_{i}') else [],
                chat_config=ChatConfig(
                    template=template,
                    prompt=os.getenv(f'PROMPT_BOT_{i}', ''),
                    tone_variable=os.getenv('TONE_VARIABLE', 'neutral'),
                    eos_token=EOS_TOKEN_MAP[AIAgents(ai_agent)],
                    token_length_array=[20, 40, 200],
                    username=os.getenv(f'USERNAME_BOT_{i}', DEFAULT_BOT_USERNAMES[i])
                )
            )
            print(f"ai-agent-{i}", self.configs.get(f'ai-agent-{i}'))

    def get_agent_config(self, id: str) -> Optional[AgentConfig]:
        return self.configs.get(id)

    def get_all_configs(self) -> List[AgentConfig]:
        return list(self.configs.values())

    def get_common_config(self) -> Dict[str, Union[str, List[int]]]:
        return {
            'env': os.getenv('NODE_ENV', 'prod'),
            'kip_guild_id': os.getenv('KIP_GUILD_ID', ''),
            'kip_test_channel_id': os.getenv('KIP_TEST_CHAN_ID', ''),
            'token_length_array': [20, 40, 200],
            'tone_variable': os.getenv('TONE_VARIABLE', 'neutral')
        }

    def update_agent_prompt(self, id: str, new_prompt: str) -> None:
        if config := self.configs.get(id):
            config.chat_config.prompt = new_prompt