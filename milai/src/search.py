from duckduckgo_search import DDGS
from loguru import logger

def get_search_results(query: str, max_results=5) -> str:
    try:
        text_search = f"javier milei {query}"
        logger.info(f"Searching for: {text_search[:50]}")

        results = DDGS().text(text_search, max_results=max_results, timelimit='w')
        # Convert search results to a formatted table string
        formatted_results = []
        for result in results:
            title = result.get('title', 'No Title')
            body = result.get('body', 'No Description')
            formatted_results.append(f"Title: {title}\nBody: {body}\n{'-'*50}")
        
        results = "\n".join(formatted_results)
        return results
    except Exception as e:
        logger.error(f"Error searching: {str(e)}")