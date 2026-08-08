from sqlalchemy.orm import Session
from app.models import Memory

def save_memory(db: Session, user_id: str, content: str):
    memory = Memory(
        user_id=user_id,
        content=content
    )

    db.add(memory)
    db.commit()
    db.refresh(memory)

    return memory

def get_memories(db: Session, user_id: str):
    return (
        db.query(Memory)
        .filter(Memory.user_id == user_id)
        .all()
    )