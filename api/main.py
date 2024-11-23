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
from langchain_text_splitters import MarkdownHeaderTextSplitter
import pymupdf4llm
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

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

def readFile():
    print('Reading File')
    md_text = pymupdf4llm.to_markdown("AdvanceVastuAndRemedies.pdf")
    with open("output.md", "w", encoding="utf-8") as file:
        file.write(md_text)
    print("Markdown text written to output.md")
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on)
    md_header_splits = markdown_splitter.split_text(md_text)
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    chunk_size = 2000
    chunk_overlap = 200
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )

    # Split
    splits = text_splitter.split_documents(md_header_splits)
    print(splits)
    return splits

def createVectorDB(chunks):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = FAISS.from_documents(chunks, embeddings)
    query = "Is it good to have bathroom in north east side of my building?"
    results = db.similarity_search(query)
    for res in results:
        print(res.page_content)
        with open("search.txt", "a", encoding="utf-8") as file:
            file.write(res.page_content)

splits = readFile()
createVectorDB(splits)
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
