from anthropic import Anthropic
from loguru import logger

# import src.context_retriever as retriever
from src.db import insert_chat_history, get_chat_history
from src.prompt import CHAT_PROMPT
from src.search import get_search_results
from utils.config import ANTHROPIC_API_KEY

client = Anthropic(
    api_key=ANTHROPIC_API_KEY,  # This is the default and can be omitted
)

def stream_antropic_response(query: str, session_id: str):
    # context = retriever.ret(query, 4)

    chat_history = get_chat_history(session_id)
    chat_history_str = ""
    for chat in reversed(chat_history):
        chat_history_str += f"{chat['sender']}: {chat['message']}\n"

    # print(f"Chat history: {chat_history_str}")
    search_results = get_search_results(query)

    full_response = ""
    with client.messages.stream(
        system=CHAT_PROMPT.format(contexto=search_results, chat_history=chat_history_str),
        max_tokens=800,
        messages=[
            {
                "role": "user",
                "content": query,
            }
        ],
        model="claude-3-5-sonnet-latest",
    ) as stream_response:
        for chunk in stream_response.text_stream:
            # Remove markdown formatting (text between asterisks)
            clean_chunk = ''
            in_asterisk = False
            for char in chunk:
                if char == '*':
                    in_asterisk = not in_asterisk
                    continue
                if not in_asterisk:
                    clean_chunk += char
            full_response += clean_chunk
            yield { 'message' : clean_chunk }
    
        yield { 'message': full_response, 'end': True }

    logger.info(f"Anthropic response: {full_response}")
    
    insert_chat_history(user_id='', message=query, sender='user', session_id=session_id)
    insert_chat_history(user_id='', message=full_response, sender='bot', session_id=session_id)
