from typing import Dict, Any, Optional
import anthropic
from openai import OpenAI
from mistralai.client import MistralClient
from dataclasses import dataclass
import requests

from base_replier import BaseReplier, ReplierConfig
from anthropic_replier import AnthropicReplier
from openai_replier import OpenAIReplier
from mistral_replier import MistralReplier
from deepseek_replier import DeepSeekReplier

@dataclass
class AgentConfig:
    id: str
    api_key: str
    api_endpoint: str
    chat_config: ReplierConfig

def create_replier(agent_config: AgentConfig) -> BaseReplier:
    """Factory function to create appropriate replier based on API endpoint."""
    
    config = ReplierConfig(
        template=agent_config.chat_config.template,
        prompt=agent_config.chat_config.prompt,
        tone_variable=agent_config.chat_config.tone_variable,
        eos_token=agent_config.chat_config.eos_token,
        token_length_array=agent_config.chat_config.token_length_array,
        env=agent_config.chat_config.env
    )

    if agent_config.api_endpoint == "anthropic":
        anthropic_client = anthropic.Anthropic(api_key=agent_config.api_key)
        return AnthropicReplier(agent_config.id, anthropic_client, config)
    
    elif agent_config.api_endpoint == "openai":
        openai_client = OpenAI(api_key=agent_config.api_key)
        return OpenAIReplier(agent_config.id, openai_client, config)
    
    elif agent_config.api_endpoint == "mistral":
        return MistralReplier(agent_config.id, agent_config.api_key, config)
    
    elif agent_config.api_endpoint == "deepseek":
        return DeepSeekReplier(agent_config.id, agent_config.api_key, config)
    
    else:
        raise ValueError(f"Unknown API endpoint: {agent_config.api_endpoint}")