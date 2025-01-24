from fastapi import FastAPI, HTTPException, WebSocket, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic
import os
from typing import Optional
import json
import logging
from dogs.utils.config import ANTHROPIC_API_KEY

app = FastAPI()
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logger = logging.getLogger("api")
logger.setLevel(logging.DEBUG)

class Message(BaseModel):
    content: str
    room_id: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    sender: str
    message: str
    type: str = "stream"
    chatbot_id: Optional[str] = None

@app.post("/chat")
async def chat_with_claude(message: Message):
    try:
        response = await client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": message.content
            }]
        )
        return {"response": response.content[0].text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/chat_with_chatroom")
async def chat_with_chatroom(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            
            try:
                response = await client.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=1024,
                    messages=[{
                        "role": "user",
                        "content": data["question"]
                    }]
                )
                
                # Send user message
                await websocket.send_json(
                    ChatResponse(
                        sender="user",
                        message=data["question"],
                        type="stream",
                        chatbot_id=data.get("room_id")
                    ).dict()
                )
                
                # Send start message
                await websocket.send_json(
                    ChatResponse(
                        sender="bot",
                        message="",
                        type="start",
                        chatbot_id=data.get("room_id")
                    ).dict()
                )
                
                # Send response content
                await websocket.send_json(
                    ChatResponse(
                        sender="bot",
                        message=response.content[0].text,
                        type="stream",
                        chatbot_id=data.get("room_id")
                    ).dict()
                )
                
                # Send end message
                await websocket.send_json(
                    ChatResponse(
                        sender="bot",
                        message="",
                        type="end",
                        chatbot_id=data.get("room_id")
                    ).dict()
                )
                
            except Exception as e:
                logger.error(f"Error in websocket communication: {str(e)}")
                await websocket.send_json(
                    ChatResponse(
                        sender="bot",
                        message="Sorry, something went wrong. Please try again.",
                        type="error"
                    ).dict()
                )
                
    except Exception as e:
        logger.error(f"WebSocket connection error: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)