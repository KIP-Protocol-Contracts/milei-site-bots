from typing import Any, Tuple
from openai import OpenAI
from base_replier import BaseReplier, ReplierConfig
from message.prompt_utilities import clean_up_response

class OpenAIReplier(BaseReplier):
    eos_token = "__"

    def __init__(self, agent_id: str, openai_client: OpenAI, config: ReplierConfig):
        super().__init__(agent_id, config)
        self.openai = openai_client

    async def call_api(self, prompt: str, max_tokens: int) -> Tuple[Any, str]:
        response = await self.openai.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-3.5-turbo"
        )

        return response, response.choices[0].message.content

    def remove_eos_token(self, reply: Any) -> Any:
        if reply.choices[0].message.content:
            reply.choices[0].message.content = reply.choices[0].message.content.replace(
                self.eos_token, ""
            )
        return reply

    def is_valid_reply(self, reply: Any) -> bool:
        return hasattr(reply, 'choices') and len(reply.choices) > 0

    def convert_to_string(self, reply: Any, max_tokens: int) -> str:
        return clean_up_response(
            reply.choices[0].message.content, 
            max_tokens
        )