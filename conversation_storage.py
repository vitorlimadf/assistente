import sqlite3
import json
from datetime import datetime
from contextlib import closing
from typing import List, Tuple, Optional

DB_PATH = "conversations.db"


def _get_conn(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    _init_db(conn)
    return conn


def _init_db(conn: sqlite3.Connection):
    with conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS conversations (
            thread_id TEXT PRIMARY KEY,
            updated_at TEXT,
            title TEXT
        )"""
        )
        # if the table already existed without the title column, try to add it
        try:
            conn.execute("ALTER TABLE conversations ADD COLUMN title TEXT")
        except sqlite3.OperationalError:
            pass
        conn.execute(
            """CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id TEXT,
            role TEXT,
            content TEXT,
            sources TEXT,
            FOREIGN KEY(thread_id) REFERENCES conversations(thread_id)
        )"""
        )




def save_conversation(
    thread_id: str,
    messages: List[dict],
    *,
    title: Optional[str] = None,
    db_path: str = DB_PATH,
):
    """Persist messages of a conversation."""
    now = datetime.now().isoformat()
    with closing(_get_conn(db_path)) as conn, conn:
        conn.execute(
            "INSERT INTO conversations(thread_id, updated_at, title) VALUES(?, ?, ?) "
            "ON CONFLICT(thread_id) DO UPDATE SET updated_at=excluded.updated_at, title=COALESCE(?, title)",
            (
                thread_id,
                now,
                title,
                title,
            ),
        )
        conn.execute("DELETE FROM messages WHERE thread_id=?", (thread_id,))
        for msg in messages:
            conn.execute(
                "INSERT INTO messages(thread_id, role, content, sources) VALUES(?, ?, ?, ?)",
                (
                    thread_id,
                    msg.get("role"),
                    msg.get("content"),
                    json.dumps(msg.get("sources")) if msg.get("sources") is not None else None,
                ),
            )


def load_conversation(thread_id: str, db_path: str = DB_PATH) -> List[dict]:
    """Retrieve messages for a conversation."""
    with closing(_get_conn(db_path)) as conn:
        rows = conn.execute(
            "SELECT role, content, sources FROM messages WHERE thread_id=? ORDER BY id",
            (thread_id,),
        ).fetchall()
    result = []
    for row in rows:
        data = {
            "role": row["role"],
            "content": row["content"],
        }
        if row["sources"]:
            data["sources"] = json.loads(row["sources"])
        result.append(data)
    return result


def list_conversations(db_path: str = DB_PATH) -> List[Tuple[str, str]]:
    """List available conversations as (thread_id, title)."""
    with closing(_get_conn(db_path)) as conn:
        rows = conn.execute(
            "SELECT thread_id, title FROM conversations ORDER BY updated_at DESC"
        ).fetchall()
    return [(row["thread_id"], row["title"] or "") for row in rows]


def delete_conversation(thread_id: str, db_path: str = DB_PATH) -> None:
    """Remove a conversation and its messages."""
    with closing(_get_conn(db_path)) as conn, conn:
        conn.execute("DELETE FROM messages WHERE thread_id=?", (thread_id,))
        conn.execute("DELETE FROM conversations WHERE thread_id=?", (thread_id,))


def rename_conversation(thread_id: str, new_title: str, db_path: str = DB_PATH) -> None:
    """Change the title of a stored conversation."""
    with closing(_get_conn(db_path)) as conn, conn:
        conn.execute(
            "UPDATE conversations SET title=?, updated_at=? WHERE thread_id=?",
            (new_title, datetime.now().isoformat(), thread_id),
        )
