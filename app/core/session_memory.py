from collections import defaultdict

import time

session_memory = defaultdict(dict)
session_expiry = {}

SESSION_TTL = 270  # Durée de vie des sessions en secondes

def store_param(session_id: str, key: str, value):
    session_memory[session_id][key] = value
    session_expiry[session_id] = time.time() + SESSION_TTL

def get_param(session_id: str, key: str):
    if session_expiry.get(session_id, 0) < time.time():
        clear_session(session_id)
        return None
    return session_memory[session_id].get(key)

def clear_session(session_id: str):
    session_memory.pop(session_id, None)
    session_expiry.pop(session_id, None)

def get_progression(session_id: str) -> dict:
    return session_memory.get(session_id, {}).get("progression", {})

def update_progression(session_id: str, key: str, value: bool):
    session = session_memory.setdefault(session_id, {})
    session.setdefault("progression", {})[key] = value

def debug_session(session_id: str):
    print(f"[SESSION DEBUG] {session_id} → {session_memory.get(session_id, {})}")
