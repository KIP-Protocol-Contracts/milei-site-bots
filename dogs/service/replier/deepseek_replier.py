from typing import Any, Tuple
import aiohttp
from base_replier import BaseReplier, ReplierConfig
from utils.prompt_utilities import clean_up_response

class DeepSeekReplier(BaseReplier):
    eos_token = "__"

    def __init__(self, agent_id: str, api_key: str, config: ReplierConfig):
        super().__init__(agent_id, config)
        self.api_key = api_key
        self.api_url = "https://api.deepseek.com/chat/completions"

    async def call_api(self, prompt: str, max_tokens: int) -> Tuple[Any, str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url, json=data, headers=headers) as response:
                response_data = await response.json()
                return response_data, response_data["generated_text"]

    def remove_eos_token(self, reply: Any) -> Any:
        reply["generated_text"] = reply["generated_text"].replace(self.eos_token, "")
        return reply

    def is_valid_reply(self, reply: Any) -> bool:
        return isinstance(reply, dict) and "generated_text" in reply

    def convert_to_string(self, reply: Any, max_tokens: int) -> str:
        return clean_up_response(reply["generated_text"], max_tokens)