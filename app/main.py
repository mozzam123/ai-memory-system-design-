from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from app.memory import get_history, add_message
from app.database import Base, engine, SessionLocal
from app.models import Memory
from app.memory_service import save_memory, get_memories
from app.vector_store import add_memory, search_memories

load_dotenv()

app = FastAPI()

Base.metadata.create_all(bind=engine)

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)


class MemoryRequest(BaseModel):
    user_id: str
    content: str


class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    message: str


@app.post("/chat")
async def chat(request: ChatRequest):
    history = get_history(request.session_id)

    db = SessionLocal()
    try:
        memories = search_memories(request.user_id, request.message, k=3)
    finally:
        db.close()

    messages = []

    if memories:
        memory_text = "\n".join(f"- {memory.page_content}" for memory in memories)

        messages.append(HumanMessage(content=f"Relevant user memories:\n{memory_text}"))

    for message in history:
        if message["role"] == "user":
            messages.append(HumanMessage(content=message["content"]))
        else:
            messages.append(AIMessage(content=message["content"]))

    messages.append(HumanMessage(content=request.message))

    response = await llm.ainvoke(messages)

    add_message(request.session_id, "user", request.message)

    add_message(request.session_id, "assistant", response.content)

    return {"session_id": request.session_id, "response": response.content}


@app.post("/memories")
async def create_memory(request: MemoryRequest):
    db = SessionLocal()

    try:
        memory = save_memory(db, request.user_id, request.content)

        add_memory(memory.id, memory.user_id, memory.content)

        return {"id": memory.id, "user_id": memory.user_id, "content": memory.content}
    finally:
        db.close()


@app.get("/memories/{user_id}")
async def list_memories(user_id: str):
    db = SessionLocal()

    try:
        memories = get_memories(db, user_id)

        return [
            {"id": memory.id, "user_id": memory.user_id, "content": memory.content}
            for memory in memories
        ]
    finally:
        db.close()
