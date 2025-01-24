from abc import ABC, abstractmethod
from typing import Any, Tuple, Optional, List
from dataclasses import dataclass
import random
import asyncio
import time

@dataclass
class ReplierConfig:
    template: str
    prompt: str 
    tone_variable: str
    eos_token: str
    token_length_array: List[int]
    env: str

class BaseReplier(ABC):
    def __init__(self, agent_id: str, config: ReplierConfig):
        self.agent_id = agent_id
        self.config = config

    @abstractmethod
    async def call_api(self, prompt: str, max_tokens: int) -> Tuple[Any, str]:
        pass

    @abstractmethod
    def is_valid_reply(self, reply: Any) -> bool:
        pass

    @abstractmethod
    def convert_to_string(self, reply: Any, max_tokens: int) -> str:
        pass

    @abstractmethod
    def remove_eos_token(self, reply: Any) -> Any:
        pass

    @property
    @abstractmethod
    def eos_token(self) -> str:
        pass

    async def recursive_call_api(self, prompt: str, max_tokens: int, eos_token: str) -> Any:
        response, response_string = await self.call_api(prompt, max_tokens)
        print(f"Received response from API:", prompt, response_string, max_tokens, eos_token)
        return self.remove_eos_token(response)

    async def reply_with_focus(self, focused_message: dict, channel_context: List[dict], 
                             max_token: int) -> Tuple[Any, str]:
        from utils.prompts import process_prompt  # Avoid circular import

        combined_prompt = process_prompt(
            template=self.config.template,
            prompt=self.config.prompt,
            chat_length_prompt=str(max_token),
            eos_token=self.eos_token,
            selected_message=focused_message,
            channel_context=channel_context,
            agent_id=self.agent_id
        )

        try:
            response = await self.recursive_call_api(combined_prompt, max_token, self.eos_token)
            return response, combined_prompt
        except Exception as error:
            print(f"Error calling API:", error)
            raise

    async def reply_general(self, channel_messages: List[dict], max_token: int) -> Tuple[Any, str]:
        print('1. reply_general')
        chat_length_prompt = str(max_token)

        print('2. reply_general')
        combined_prompt = process_prompt(
            template=self.config.template,
            prompt=self.config.prompt,
            chat_length_prompt=chat_length_prompt,
            eos_token=self.eos_token,
            selected_message=None,
            channel_context=channel_messages,
            agent_id=self.agent_id
        )

        print('3. reply_general')
        try:
            print('4. reply_general')
            response = await self.recursive_call_api(combined_prompt, max_token, self.eos_token)
            print('5. reply_general')
            return response, combined_prompt
        except Exception as error:
            print(f"Error calling API:", error)
            raise

    async def attempt_human_like_post(self, channel, controller) -> None:
        try:
            if controller.aborted:
                raise Exception('Aborted')

            # Get recent messages
            recent_messages = self.filter_old_messages(
                await channel.fetch_messages(limit=10),
                10
            )
            print('2. filtered recent messages')

            if controller.aborted:
                raise Exception('Aborted')

            max_tokens = self.config.token_length_array[2]
            print('3. got a random maxToken')

            ai_reply, full_prompt = await self.reply_general(recent_messages, max_tokens)
            print('4. got an AI reply')

            ai_reply_string = self.convert_to_string(ai_reply, max_tokens)
            response_message = self.wrap_response(ai_reply_string, full_prompt)
            print('5. wrapped response')

            # Simulate typing
            await channel.trigger_typing()
            print('6. sent typing indicator')
            await asyncio.sleep(len(ai_reply_string) * 0.05)  # 50ms per character
            print('7. waited for human typing speed')
            
            if controller.aborted:
                raise Exception('Aborted')

            await self.send_message_in_chunks(channel, response_message)
            print('8. sent message in chunks')

        except Exception as error:
            if str(error) == "Aborted":
                raise
            print("Error in attempt_human_like_post:", error)
            raise

    def wrap_response(self, response: str, full_prompt: str) -> str:
        if self.config.env == 'dev':
            return f"""{response}
```
=====THIS PART OF THE MESSAGE WILL BE IGNORED BY THE OTHER AND SELF BOTS=====
=====FULL PROMPT=====
{full_prompt}
=====METADATA=====
{{"agentId": "{self.agent_id}", "config": {self.config}}}
```"""
        return response

    async def send_message_in_chunks(self, channel, message: str) -> None:
        chunk_size = 2000  # Discord's max message length
        for i in range(0, len(message), chunk_size):
            chunk = message[i:i + chunk_size]
            await channel.send(chunk)

    def get_random_delay(self, min_val: int, max_val: int) -> int:
        return random.randint(min_val, max_val)

    @staticmethod
    def filter_old_messages(messages: List[dict], minutes: int) -> List[dict]:
        cutoff_time = time.time() - (minutes * 60)
        return [msg for msg in messages if msg['created_timestamp'] > cutoff_time]