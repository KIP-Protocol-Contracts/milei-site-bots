from typing import Any, Tuple
import anthropic
from base_replier import BaseReplier, ReplierConfig
from utils.prompt_utilities import clean_up_response

class AnthropicReplier(BaseReplier):
    eos_token = "__"

    def __init__(self, agent_id: str, anthropic_client: anthropic.Anthropic, 
                 config: ReplierConfig):
        super().__init__(agent_id, config)
        self.anthropic = anthropic_client

    async def call_api(self, prompt: str, max_tokens: int) -> Tuple[Any, str]:
        response = await self.anthropic.messages.create(
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
            model="claude-3-5-sonnet-20240620"
        )

        print(f"Anthropic: Received response from API:", response)
        return response, response.content[0].text

    def remove_eos_token(self, reply: Any) -> Any:
        reply.content[0].text = reply.content[0].text.replace(self.eos_token, "")
        return reply

    def is_valid_reply(self, reply: Any) -> bool:
        return hasattr(reply, 'content') and len(reply.content) > 0

    def convert_to_string(self, reply: Any, max_tokens: int) -> str:
        return clean_up_response(reply.content[0].text, max_tokens)