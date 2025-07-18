import json
import os
from datetime import datetime

FILE_PATH = "conversations.json"


def _load_all():
    if os.path.exists(FILE_PATH):
        try:
            with open(FILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def _save_all(data):
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f)


def save_conversation(thread_id: str, messages: list):
    """Save messages of a conversation."""
    data = _load_all()
    data[thread_id] = {
        "messages": messages,
        "updated_at": datetime.now().isoformat()
    }
    _save_all(data)


def load_conversation(thread_id: str) -> list:
    """Load messages for a specific conversation."""
    data = _load_all()
    conv = data.get(thread_id)
    if conv:
        return conv.get("messages", [])
    return []


def list_conversations() -> list:
    """Return list of (thread_id, updated_at)."""
    data = _load_all()
    return [
        (tid, info.get("updated_at"))
        for tid, info in data.items()
    ]
