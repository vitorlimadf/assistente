import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from conversation_storage import (
    save_conversation,
    load_conversation,
    list_conversations,
    FILE_PATH,
)


def test_save_and_load(tmp_path, monkeypatch):
    path = tmp_path / "conv.json"
    monkeypatch.setattr("conversation_storage.FILE_PATH", str(path))

    tid = "thread1"
    messages = [{"role": "user", "content": "oi"}]

    save_conversation(tid, messages)
    assert load_conversation(tid) == messages

    convs = list_conversations()
    assert convs and convs[0][0] == tid

