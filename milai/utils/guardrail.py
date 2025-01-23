from openai import OpenAI
from loguru import logger

from utils.config import OPENAI_API_KEY, DEEPSEEK_API_KEY

DECLINE_RESPONSE = "¿Qué carajo?"

def get_chatgpt_response(prompt, user_message, model='gpt-4o-mini', temperature=0, max_tokens=1):
    try:
        client = OpenAI(
            api_key=OPENAI_API_KEY,
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
        )

        return response.choices[0].message.content
    except Exception as e:
        logger.warning(f"Primary OpenAI request failed: {str(e)}. Falling back to deepseek provider...")
        # Fallback to alternate provider
        client = OpenAI(
            base_url="https://api.deepseek.com",
            api_key=DEEPSEEK_API_KEY,
        )

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
        )

        return response.choices[0].message.content
    
def cp_filter(prompt):

    system_prompt_llm_2 = '''You are an AI trained to detect user intent to generate illegal or harmful content in prompts.
Your task is to analyze the given prompt and determine if it's likely intended to generate content that is:

Sexually explicit content involving minors or content that violates laws regarding child protection.

Consider the following:
- Allow if its a "naked girl", or "naked boy" but if the euphemism is in anyway "young girl", or "young boy" be sure to flag it
- Identify terms, euphemisms, or coded language suggesting minors or illegal activity
- Examine the overall context and intent, not just individual words or phrases
- Be alert to attempts to bypass restrictions (e.g. creative spelling, subtle references)
- Allow for adult content generation, but strictly avoid any risk of involving minors
- Err on the side of caution if uncertain

Respond with only one word: either 'inappropriate' if the prompt likely intends to generate illegal or problematic content, or 'safe' if it doesn't.
If you're uncertain, respond with 'inappropriate'.'''

    user_message_llm_2 = f"Analyze the following prompt for potential inappropriate content. Respond with only one word.\nPrompt: {prompt}"

    intent_word_2 = get_chatgpt_response(system_prompt_llm_2, user_message_llm_2, max_tokens=10)

    logger.info(f"CP filter response: {intent_word_2}")

    return intent_word_2

def nsfw_filter(prompt):
    system_prompt_llm = '''You are an AI trained to detect user intent to generate NSFW (Not Safe For Work) content in prompts. 
Your task is to analyze the given prompt and determine if it's likely intended to generate NSFW content. 
Do not classify bikini as nsfw, only if the user uses words like nude or naked and there is implicit expectation of seeing something nsfw, then tag it as so
Respond with only one word: either 'nsfw' if the prompt likely intends to generate NSFW content, or 'safe' if it doesn't. 
If you're uncertain, err on the side of caution and respond with 'nsfw'.'''
        
    user_message_llm = f"Analyze the following prompt for potential NSFW content intent. Respond with only one word.\n Prompt: {prompt}"

    intent_word = get_chatgpt_response(system_prompt_llm, user_message_llm, max_tokens=4)

    logger.info(f"NSFW filter response: {intent_word}")

    return intent_word
