# =====================================================
#  database/conversations.py
#  Stores and retrieves real conversation history
# =====================================================

import json
import os
import uuid
from datetime import datetime

# Path to store conversation data
DB_PATH = os.path.join(os.path.dirname(__file__), "conversations_db.json")


def _load_db() -> dict:
    """Load the entire database from file."""
    if not os.path.exists(DB_PATH):
        return {}
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_db(data: dict):
    """Save the entire database to file."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_conversation(user_id: str, title: str, messages: list) -> str:
    """
    Save or update a conversation for a user.
    Returns the conversation_id.
    """
    db = _load_db()

    if user_id not in db:
        db[user_id] = {}

    # Generate a new conversation id
    conv_id = str(uuid.uuid4())[:8]

    db[user_id][conv_id] = {
        "id":         conv_id,
        "title":      title[:50],   # Truncate long titles
        "messages":   messages,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    _save_db(db)
    return conv_id


def update_conversation(user_id: str, conv_id: str, messages: list, title: str = None):
    """Update messages in an existing conversation."""
    db = _load_db()

    if user_id not in db or conv_id not in db[user_id]:
        return False

    db[user_id][conv_id]["messages"]   = messages
    db[user_id][conv_id]["updated_at"] = datetime.now().isoformat()

    if title:
        db[user_id][conv_id]["title"] = title[:50]

    _save_db(db)
    return True


def get_recent_conversations(user_id: str, limit: int = 10) -> list:
    """
    Get the most recent conversations for a user.
    Returns a list sorted by updated_at descending.
    """
    db = _load_db()

    if user_id not in db:
        return []

    convs = list(db[user_id].values())

    # Sort by updated_at descending
    convs.sort(key=lambda x: x.get("updated_at", ""), reverse=True)

    # Return limited results with friendly time labels
    result = []
    for c in convs[:limit]:
        result.append({
            "id":         c["id"],
            "title":      c["title"],
            "updated_at": c["updated_at"],
            "time_label": _time_label(c["updated_at"]),
            "preview":    _get_preview(c["messages"]),
        })

    return result


def get_conversation(user_id: str, conv_id: str) -> dict:
    """Get a single full conversation by id."""
    db = _load_db()

    if user_id not in db or conv_id not in db[user_id]:
        return None

    return db[user_id][conv_id]


def delete_conversation(user_id: str, conv_id: str) -> bool:
    """Delete a conversation."""
    db = _load_db()

    if user_id not in db or conv_id not in db[user_id]:
        return False

    del db[user_id][conv_id]
    _save_db(db)
    return True


def _get_preview(messages: list) -> str:
    """Get first user message as preview text."""
    for msg in messages:
        if msg.get("role") == "user":
            content = msg.get("content", "")
            return content[:60] + "..." if len(content) > 60 else content
    return ""


def _time_label(iso_timestamp: str) -> str:
    """Convert ISO timestamp to friendly label like 'Today', 'Yesterday', 'Mon'."""
    try:
        dt    = datetime.fromisoformat(iso_timestamp)
        now   = datetime.now()
        delta = now - dt

        if delta.days == 0:
            return "Today"
        elif delta.days == 1:
            return "Yesterday"
        elif delta.days < 7:
            return dt.strftime("%a")   # Mon, Tue, Wed...
        elif delta.days < 30:
            return f"{delta.days // 7}w ago"
        else:
            return dt.strftime("%b %d")  # Jan 15
    except Exception:
        return ""