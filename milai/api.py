import sys

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from loguru import logger
from loguru._defaults import LOGURU_FORMAT

from src.anthropic_response import stream_antropic_response
from utils.guardrail import cp_filter, nsfw_filter, DECLINE_RESPONSE

import json

logger.remove()
logger.add(
    sys.stdout,
    format=str(LOGURU_FORMAT),
)  # type: ignore

app = FastAPI()

@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_json()
            logger.info(f"Received data: {data}")
            query = data.get('query')
            session_id = data.get('session_id')
            
            # Check content filters
            cp_result = cp_filter(query)
            nsfw_result = nsfw_filter(query)
            
            if cp_result == 'inappropriate' or nsfw_result == 'nsfw':
                logger.warning(f"Declining response due to content filter: {cp_result} {nsfw_result}")
                await websocket.send_json({"message": DECLINE_RESPONSE})
                continue
                
            stream = stream_antropic_response(query, session_id)
            for chunk in stream:
                if isinstance(chunk, dict) and 'error' in chunk:
                    raise Exception(chunk['error'])
                await websocket.send_json(chunk)
            
        except json.JSONDecodeError:
            logger.error("WebSocket error: Invalid JSON received")
            break
        except ConnectionError as e:
            logger.error(f"WebSocket connection error: {e}")
            break
        except WebSocketDisconnect:
            logger.info("WebSocket disconnected")
            break
        except Exception as e:
            logger.error(f"WebSocket error: {str(e)}")
            break
