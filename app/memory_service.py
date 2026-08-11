from sqlalchemy.orm import Session

from app.models import Memory


def save_memory(db: Session, user_id: str, content: str):
    memory = Memory(user_id=user_id, content=content)

    db.add(memory)
    db.commit()
    db.refresh(memory)

    return memory


def get_memories(db: Session, user_id: str):
    return db.query(Memory).filter(Memory.user_id == user_id).all()


def update_memory(db: Session, memory_id: int, user_id: str, content: str):
    memory = (
        db.query(Memory)
        .filter(
            Memory.id == memory_id, Memory.user_id == user_id, Memory.is_active == True
        )
        .first()
    )

    if not memory:
        return None

    memory.content = content
    db.commit()
    db.refresh(memory)

    return memory


def delete_memory(db: Session, memory_id: int, user_id: str):
    memory = (
        db.query(Memory)
        .filter(
            Memory.id == memory_id, Memory.user_id == user_id, Memory.is_active == True
        )
        .first()
    )

    if not memory:
        return None

    memory.is_active = False
    db.commit()

    return memory
