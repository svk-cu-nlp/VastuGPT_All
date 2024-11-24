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
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

# Load environment variables
load_dotenv()

# Initialize LangChain Groq model
groq_model = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="llama-3.2-90b-text-preview")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
# Initialize FastAPI app
app = FastAPI()
global db
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
    db = FAISS.from_documents(chunks, embeddings)
    db.save_local('vastuDB')
    # query = "Is it good to have bathroom in north east side of my building?"
    # results = db.similarity_search(query)
    # for res in results:
    #     print(res.page_content)
    #     with open("search.txt", "a", encoding="utf-8") as file:
    #         file.write(res.page_content)

import textwrap

def wrap_text_preserve_newlines(text, width=110):
    # Split the input text into lines based on newline characters
    lines = text.split('\n')

    # Wrap each line individually
    wrapped_lines = [textwrap.fill(line, width=width) for line in lines]

    # Join the wrapped lines back together using newline characters
    wrapped_text = '\n'.join(wrapped_lines)
    wrapped_text_string = str(wrapped_text)

    return wrapped_text_string

def process_llm_response(llm_response):
    response = wrap_text_preserve_newlines(llm_response['result'])
    print(response)
    return response

def RAG_QA(question):
    vastuDB = FAISS.load_local(
        "vastuDB", embeddings, allow_dangerous_deserialization=True
    )
    vastu_retriever = vastuDB.as_retriever(search_kwargs={"k": 5})
    template = """
    Use the following context (delimited by <ctx></ctx>) and the chat history (delimited by <hs></hs>) to answer the question:
    ------
    <ctx>
    {context}
    </ctx>
    ------
    {question}
    Answer:
    """
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=template,
    )
    vastu_qa_chain = RetrievalQA.from_chain_type(llm=groq_model,
                                  chain_type="stuff",
                                  retriever=vastu_retriever,
                                       chain_type_kwargs={
                                            "verbose": False,
                                            "prompt": prompt,
                                        }
                                    )
    
    llm_response = vastu_qa_chain(question)
    response = process_llm_response(llm_response)
    return response

# splits = readFile()
# print(splits)
# createVectorDB(splits)
# question = "Is it good to have bathroom in north east side of my building?"
# response = RAG_QA(question)
# @app.post("/api/chat")
# async def chat(request: Request, chat_request: ChatRequest):
#     try:
#         # Convert messages to LangChain format
#         langchain_messages = []
#         for msg in chat_request.messages:
#             if msg.role == "system":
#                 langchain_messages.append(SystemMessage(content=msg.content))
#             elif msg.role == "user":
#                 langchain_messages.append(HumanMessage(content=msg.content))
#             elif msg.role == "assistant":
#                 langchain_messages.append(AIMessage(content=msg.content))

#         # Generate a response using the Groq model
#         response = groq_model(messages=langchain_messages)

#         return {
#             "role": "assistant",
#             "content": response.content,
#             "timestamp": datetime.now().isoformat()
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.post("/api/chat")
async def chat(request: Request, chat_request: ChatRequest):
    try:
        # Build chat history from all previous messages
        chat_history = ""
        for msg in chat_request.messages:
            if msg.role == "user":
                chat_history += f"User: {msg.content}\n"
            elif msg.role == "assistant":
                chat_history += f"Assistant: {msg.content}\n"

        # Extract the latest user question
        latest_user_message = next(
            (msg.content for msg in reversed(chat_request.messages) if msg.role == "user"), None
        )

        if not latest_user_message:
            raise HTTPException(status_code=400, detail="No user message provided.")

        # Construct context for RAG_QA using chat history and latest question
        context = f"{chat_history}\nUser's Question: {latest_user_message}"

        # Pass the constructed context to RAG_QA
        response = RAG_QA(question=context)

        return {
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}
