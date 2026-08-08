import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from app.memory import get_history, add_message

load_dotenv()

app = FastAPI()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)

class ChatRequest(BaseModel):
    session_id: str
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    history = get_history(request.session_id)

    messages = []

    for message in history:
        if message["role"] == "user":
            messages.append(HumanMessage(content=message["content"]))
        else:
            messages.append(AIMessage(content=message["content"]))

    messages.append(HumanMessage(content=request.message))

    response = await llm.ainvoke(messages)

    add_message(
        request.session_id,
        "user",
        request.message
    )

    add_message(
        request.session_id,
        "assistant",
        response.content
    )

    return {
        "session_id": request.session_id,
        "response": response.content
    }