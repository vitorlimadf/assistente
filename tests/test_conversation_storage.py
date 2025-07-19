import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from conversation_storage import (
    save_conversation,
    load_conversation,
    list_conversations,
)


def test_save_and_load(tmp_path, monkeypatch):
    path = tmp_path / "conv.db"

    tid = "thread1"
    messages = [{"role": "user", "content": "oi"}]

    save_conversation(tid, messages, db_path=str(path))
    assert load_conversation(tid, db_path=str(path)) == messages

    convs = list_conversations(db_path=str(path))
    assert convs and convs[0][0] == tid

