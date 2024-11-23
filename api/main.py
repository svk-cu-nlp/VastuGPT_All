from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from langchain_groq import ChatGroq
from datetime import datetime
# from langchain.chat_models import ChatGroq
from langchain.schema import AIMessage, HumanMessage, SystemMessage
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize LangChain Groq model
groq_model = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="llama-3.2-90b-text-preview")

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
        # Convert messages to LangChain format
        langchain_messages = []
        for msg in chat_request.messages:
            if msg.role == "system":
                langchain_messages.append(SystemMessage(content=msg.content))
            elif msg.role == "user":
                langchain_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                langchain_messages.append(AIMessage(content=msg.content))

        # Generate a response using the Groq model
        response = groq_model(messages=langchain_messages)

        return {
            "role": "assistant",
            "content": response.content,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}
