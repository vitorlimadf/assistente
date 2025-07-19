import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from conversation_storage import (
    save_conversation,
    load_conversation,
    list_conversations,
    delete_conversation,
    rename_conversation,
)


def test_save_and_load(tmp_path, monkeypatch):
    path = tmp_path / "conv.db"

    tid = "thread1"
    messages = [{"role": "user", "content": "oi"}]

    save_conversation(tid, messages, title="titulo", db_path=str(path))
    assert load_conversation(tid, db_path=str(path)) == messages

    convs = list_conversations(db_path=str(path))
    assert convs and convs[0] == (tid, "titulo")


def test_rename_and_delete(tmp_path):
    path = tmp_path / "conv.db"
    tid = "t1"
    msgs = [{"role": "assistant", "content": "hi"}]
    save_conversation(tid, msgs, title="old", db_path=str(path))

    rename_conversation(tid, "novo", db_path=str(path))
    convs = list_conversations(db_path=str(path))
    assert convs == [(tid, "novo")]

    delete_conversation(tid, db_path=str(path))
    assert list_conversations(db_path=str(path)) == []

