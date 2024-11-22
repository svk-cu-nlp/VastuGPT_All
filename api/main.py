from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize FastAPI app
app = FastAPI()

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str
    timestamp: datetime

class ChatRequest(BaseModel):
    messages: List[Message]
    stream: Optional[bool] = False

@app.post("/api/chat")
@limiter.limit("60/minute")
async def chat(request: Request, chat_request: ChatRequest):
    try:
        # Convert our messages to OpenAI format
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in chat_request.messages
        ]

        # If streaming is requested
        if chat_request.stream:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=openai_messages,
                stream=True
            )

            async def generate():
                async for chunk in response:
                    if chunk.choices[0].delta.content is not None:
                        yield chunk.choices[0].delta.content

            return StreamingResponse(generate(), media_type="text/event-stream")

        # Non-streaming response
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=openai_messages
        )

        return {
            "role": "assistant",
            "content": response.choices[0].message.content,
            "timestamp": datetime.now().isoformat()
        }

    except openai.APIError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}