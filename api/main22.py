# uvicorn main:app --reload
from langchain_cohere import ChatCohere
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
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

# Access the API key
cohere_api_key = os.getenv("COHERE_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")
# Creating LLM instances
llm = ChatCohere(
    model="command-r-plus-08-2024",
    cohere_api_key=cohere_api_key,
    MAX_TOKENS=120000

)

gemini_model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", api_key=google_api_key,
                             temperature=0.3, max_tokens=400000)


import cohere

co = cohere.ClientV2()

response = co.chat(
    model="command-r-plus-08-2024",
    messages=[{"role": "user", "content": "hello world!"}],
)

print(response)

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
        # Convert our messages to OpenAI format
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in chat_request.messages
        ]
        

        # If streaming is requested
        if chat_request.stream:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
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
            model="gpt-4o-mini",
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
