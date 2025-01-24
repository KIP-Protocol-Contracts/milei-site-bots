from typing import Optional, List, Dict, Any
import re
from datetime import datetime, timedelta

def process_prompt(
    template: str,
    prompt: str,
    chat_length_prompt: str,
    eos_token: str,
    selected_message: Optional[Dict[str, Any]] = None,
    channel_context: Optional[List[Dict[str, Any]]] = None,
    agent_id: str = ""
) -> str:
    try:
        processed_prompt = (prompt
            .replace("{eos_token}", eos_token)
            .replace("{length_variable}", chat_length_prompt)
            .replace("{tone_variable}", "neutral"))  # Could be configurable

        processed_channel_context = (
            sanitize_channel_context(channel_context, agent_id)
            if channel_context else ""
        )

        processed_selected_message = (
            prompt_message_format(selected_message, agent_id)
            if selected_message else ""
        )

        result = (process_new_lines(template)
            .replace("{Prompt}", process_new_lines(processed_prompt))
            .replace("{ChannelContext}", processed_channel_context)
            .replace("{SelectedMessage}", processed_selected_message))

        return result

    except Exception as error:
        print("Error in process_prompt:", error)
        raise

def sanitize_channel_context(messages: List[Dict[str, Any]], agent_id: str) -> str:
    try:
        reversed_context = messages[::-1]
        sanitized_context_array = []

        for message in reversed_context:
            if not isinstance(message.get('content'), str):
                raise ValueError("Invalid message content type")
            
            sanitized_message = prompt_message_format(message, agent_id)
            if sanitized_message:
                sanitized_context_array.append(sanitized_message)

        return "\n".join(sanitized_context_array)

    except Exception as error:
        print("Error in sanitize_channel_context:", error)
        raise

def prompt_message_format(message: Dict[str, Any], agent_id: str) -> str:
    try:
        if message['content'].startswith("!"):
            return ""

        left_side = "You" if message['author']['id'] == agent_id else f"User {message['author']['display_name']}"
        return f"{left_side}: {clean_discord_message(message['content'])}"

    except Exception as error:
        print("Error in prompt_message_format:", error)
        raise

def clean_discord_message(msg: str) -> str:
    try:
        # Remove mentions
        cleaned = re.sub(r'<@\d+>\s*', '', msg)

        # Remove code blocks
        cleaned = re.sub(r'```[\s\S]*?```', '', cleaned)

        # Remove inline code
        cleaned = re.sub(r'`[^`]*`', '', cleaned)

        # Remove debug sections
        cleaned = re.sub(r'\{debug:[\s\S]*?\}', '', cleaned)

        return cleaned.strip()

    except Exception as error:
        print("Error in clean_discord_message:", error)
        raise

def process_new_lines(text: str) -> str:
    return text.replace("\n\n", "<2N>").replace("\n", "").replace("<2N>", "\n")

def clean_up_response(response: Optional[str], max_tokens: int) -> str:
    if not response:
        return ""

    end_sentence_regex = r'[.!?\n]|[\U0001F600-\U0001F64F]|[\U0001F680-\U0001F6FF]|[\U0001F300-\U0001F5FF]|[\U0001F700-\U0001F77F]|[\U0001F780-\U0001F7FF]|[\U0001F800-\U0001F8FF]|[\U0001F900-\U0001F9FF]|[\U0001FA00-\U0001FA6F]|[\U0001FA70-\U0001FAFF]|[\U0001FB00-\U0001FBFF]'
    greeting_regex = re.compile(r'^yo\s+\w+\n', re.IGNORECASE)
    tone_variable_regex = re.compile(r'\{tone_variable:.*?\}\n?')
    length_variable_regex = re.compile(r'\{length_variable:.*?\}\n?')

    cleaned = response.strip()
    cleaned = tone_variable_regex.sub('', cleaned)
    cleaned = length_variable_regex.sub('', cleaned)

    is_short_response = max_tokens < 100

    if is_short_response:
        # For short responses, keep only until first comma
        comma_index = cleaned.find(',')
        if comma_index != -1:
            cleaned = cleaned[:comma_index].strip()
    else:
        # For longer responses, remove greeting and ensure proper ending
        cleaned = greeting_regex.sub('', cleaned)

        # Find last sentence ending
        matches = list(re.finditer(end_sentence_regex, cleaned, re.UNICODE))
        if matches:
            last_match = matches[-1]
            cleaned = cleaned[:last_match.end()].strip()

    # Remove trailing comma
    if cleaned.endswith(','):
        cleaned = cleaned[:-1].strip()

    return cleaned

def filter_old_messages(messages: List[Dict[str, Any]], minutes: int) -> List[Dict[str, Any]]:
    cutoff_time = datetime.now() - timedelta(minutes=minutes)
    return [
        message for message in messages 
        if datetime.fromtimestamp(message['created_timestamp']) > cutoff_time
    ]