from backend.models import Memory
from backend.database import db_session

def store_memory(user_id, key, value, investigation_id=None):
    mem = Memory(user_id=user_id, key=key, value=value, investigation_id=investigation_id)
    db_session.add(mem)
    db_session.commit()
    return mem.id

def recall_memories(user_id, query, limit=10):
    return Memory.query.filter(Memory.user_id == user_id, (Memory.key.contains(query) | Memory.value.contains(query))).limit(limit).all()

def get_investigation_memories(investigation_id):
    return Memory.query.filter_by(investigation_id=investigation_id).all()

def get_all_memories(user_id):
    return Memory.query.filter_by(user_id=user_id).all()

def clear_memory(memory_id):
    Memory.query.filter_by(id=memory_id).delete()
    db_session.commit()
