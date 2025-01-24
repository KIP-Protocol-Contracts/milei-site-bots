from typing import Any, Tuple
from mistralai.client import MistralClient
from base_replier import BaseReplier, ReplierConfig
from utils.prompt_utilities import clean_up_response

class MistralReplier(BaseReplier):
    eos_token = "</end>"

    def __init__(self, agent_id: str, api_key: str, config: ReplierConfig):
        super().__init__(agent_id, config)
        self.mistral = MistralClient(api_key=api_key)

    async def call_api(self, prompt: str, max_tokens: int) -> Tuple[Any, str]:
        response = await self.mistral.chat(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            top_p=1
        )

        return response, response.choices[0].message.content

    def remove_eos_token(self, reply: Any) -> Any:
        reply.choices[0].message.content = reply.choices[0].message.content.replace(
            self.eos_token, ""
        )
        return reply

    def is_valid_reply(self, reply: Any) -> bool:
        return (
            hasattr(reply, 'choices') and 
            len(reply.choices) > 0 and 
            hasattr(reply.choices[0], 'message')
        )

    def convert_to_string(self, reply: Any, max_tokens: int) -> str:
        return clean_up_response(reply.choices[0].message.content, max_tokens)