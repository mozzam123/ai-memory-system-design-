import logging

from dotenv import load_dotenv
from fastapi import FastAPI
from langchain_core.messages import AIMessage, HumanMessage
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from app.config import MAX_RELEVANT_MEMORIES
from app.database import Base, SessionLocal, engine
from app.memory import add_message, get_history
from app.memory_service import get_memories, save_memory
from app.vector_store import add_memory, search_memories

logger = logging.getLogger(__name__)

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


class MemoryDecision(BaseModel):
    should_save: bool = Field(
        description="Whether this information is useful as long-term user memory."
    )
    memory: str | None = Field(
        default=None,
        description="A concise statement of the user information worth remembering.",
    )


memory_llm = llm.with_structured_output(MemoryDecision)


@app.post("/chat")
async def chat(request: ChatRequest):
    memory_decision = await extract_memory(request.message)
    if memory_decision.should_save and memory_decision.memory:
        db = SessionLocal()

        try:
            memory = save_memory(db, request.user_id, memory_decision.memory)
            logger.info("Memory decision: should_save=%s", memory_decision.should_save)

            add_memory(memory.id, memory.user_id, memory.content)

        finally:
            db.close()
    history = get_history(request.session_id)

    db = SessionLocal()
    try:
        memories = search_memories(
            request.user_id, request.message, k=MAX_RELEVANT_MEMORIES
        )
        logger.info("Retrieved %d memories for user %s", len(memories), request.user_id)
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


async def extract_memory(message: str):
    prompt = f"""
Decide whether the following user message contains useful
long-term information about the user.

Save things such as:
- preferences
- interests
- goals
- skills
- important personal facts
- technology preferences

Do not save:
- questions
- temporary requests
- greetings
- jokes
- general knowledge
- information that is not about the user

If it should be saved, rewrite it as one concise user-specific memory.

User message:
{message}
"""

    return await memory_llm.ainvoke(prompt)
