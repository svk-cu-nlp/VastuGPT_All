from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
import cohere
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Cohere client
client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))

# Initialize FastAPI app
app = FastAPI()

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
async def chat(request: Request, chat_request: ChatRequest):
    try:
        # Combine messages into a single prompt for Cohere
        prompt = "\n".join([f"{msg.role}: {msg.content}" for msg in chat_request.messages])
        prompt += "\nassistant:"

        # Cohere response
        response = client.generate(
            model="command-r-plus-08-2024",
            prompt=prompt,
            max_tokens=3000,
            temperature=0.7
        )

        return {
            "role": "assistant",
            "content": response.generations[0].text.strip(),
            "timestamp": datetime.now().isoformat()
        }

    except cohere.CohereError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}
