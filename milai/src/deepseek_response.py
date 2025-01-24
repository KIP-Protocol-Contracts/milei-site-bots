from datetime import datetime
from openai import OpenAI
from loguru import logger

# import src.context_retriever as retriever
from src.db import insert_chat_history, get_chat_history
from src.prompt import CHAT_PROMPT
from src.search import get_search_results
from utils.config import DEEPSEEK_API_KEY

client = OpenAI(
    base_url="https://api.deepseek.com",
    api_key=DEEPSEEK_API_KEY,
)

def stream_deepseek_response(query: str, session_id: str):
    # context = retriever.ret(query, 4)

    chat_history = get_chat_history(session_id)
    chat_history_str = ""
    for chat in reversed(chat_history):
        chat_history_str += f"{chat['sender']}: {chat['message']}\n"

    search_results = get_search_results(query, max_results=10)
    
    month_names = [
         "enero", "febrero", "marzo", "abril", "mayo", "junio",
         "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
     ]
    today = datetime.now()
    current_date = f"{today.day} de {month_names[today.month - 1]} de {today.year}"

    full_response = ""
    stream = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": CHAT_PROMPT.format(
                contexto=search_results,
                chat_history=chat_history_str,
                current_date=current_date
            )},
            {"role": "user", "content": query}
        ],
        max_tokens=800,
        stream=True
    )
    
    for chunk in stream:
        if chunk.choices[0].delta.content:
            # Remove markdown formatting (text between asterisks)
            clean_chunk = ''
            in_asterisk = False
            for char in chunk.choices[0].delta.content:
                if char == '*':
                    in_asterisk = not in_asterisk
                    continue
                if not in_asterisk:
                    clean_chunk += char
            full_response += clean_chunk
            yield {'message': clean_chunk}
    
    yield {'message': full_response, 'end': True}

    logger.info(f"Deepseek response: {full_response}")
    
    insert_chat_history(user_id='', message=query, sender='user', session_id=session_id)
    insert_chat_history(user_id='', message=full_response, sender='bot', session_id=session_id)
