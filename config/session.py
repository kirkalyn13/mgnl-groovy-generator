import os
import json
from uuid import uuid4
from datetime import datetime, timedelta
import asyncio

# Try to connect to Redis if configured
redis_client = None
try:
    import redis
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        redis_client = redis.from_url(redis_url)
        redis_client.ping()
except Exception:
    redis_client = None

USING_REDIS = redis_client is not None
SESSION_TTL = int(os.getenv("SESSION_TTL_MINUTES", 30))
SESSION_SIZE = int(os.getenv("SESSION_SIZE", 10))

# --- Redis backend ---
def _redis_get(session_id: str) -> dict:
    """Retrieve a session from Redis by session ID. Returns None if not found or expired."""
    data = redis_client.get(f"session:{session_id}")
    return json.loads(data) if data else None

def _redis_set(session_id: str, session: dict):
    """Persist a session to Redis with a TTL defined by SESSION_TTL_MINUTES."""
    redis_client.setex(
        f"session:{session_id}",
        timedelta(minutes=SESSION_TTL),
        json.dumps(session)
    )


# --- Unified API ---
def create_session() -> tuple[str, dict]:
    """Create a new session with a unique ID and empty history.
    Persists to Redis if available, otherwise returns the session dict for in-memory storage.
    Returns a tuple of (session_id, session)."""
    session_id = str(uuid4())
    session = {"id": session_id, "history": [], "last_active": datetime.now().isoformat()}
    if USING_REDIS:
        _redis_set(session_id, session)
    return session_id, session

def get_session(sessions: dict, session_id: str) -> dict | None:
    """Retrieve a session by ID from Redis or the in-memory store.
    Returns None if the session does not exist or has expired."""
    if USING_REDIS:
        return _redis_get(session_id)
    return sessions.get(session_id)

def add_to_session(sessions: dict, session_id: str, query: str, script: str):
    """Append a query and its generated script to the session history.
    Trims history to the last SESSION_SIZE entries and updates last_active timestamp.
    Persists changes to Redis or in-memory store accordingly."""
    session = get_session(sessions, session_id)
    if not session:
        return
    session["last_active"] = datetime.now().isoformat()
    session["history"].append({"query": query, "script": script})
    session["history"] = session["history"][-SESSION_SIZE:]
    if USING_REDIS:
        _redis_set(session_id, session)
    else:
        sessions[session_id] = session

def format_history(session: dict) -> str:
    """Format session history into a prompt-friendly string.
    Returns an empty string if the session is empty or has no history."""
    if not session or not session["history"]:
        return ""
    lines = ["Previous queries and scripts in this session:"]
    for entry in session["history"]:
        lines.append(f"- Query: {entry['query']}")
        lines.append(f"  Script: {entry['script'][:200]}...")
    return "\n".join(lines)


# --- In-memory cleanup (only used when Redis is not available) ---
async def cleanup_loop(app):
    """Background task that periodically evicts expired in-memory sessions.
    Runs every 5 minutes and removes sessions inactive beyond SESSION_TTL_MINUTES.
    Only active when Redis is not configured."""
    while True:
        await asyncio.sleep(300)  # every 5 mins
        cutoff = datetime.now() - timedelta(minutes=SESSION_TTL)
        expired = [
            k for k, v in app.state.sessions.items()
            if datetime.fromisoformat(v["last_active"]) < cutoff
        ]
        for k in expired:
            del app.state.sessions[k]