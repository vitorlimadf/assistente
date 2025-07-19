import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from conversation_storage import (
    save_conversation,
    load_conversation,
    list_conversations,
    delete_conversation,
    rename_conversation,
    search_conversations,
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


def test_search_conversations(tmp_path):
    path = tmp_path / "conv.db"
    tid1 = "c1"
    tid2 = "c2"
    save_conversation(tid1, [{"role": "user", "content": "foo bar"}], title="saudações", db_path=str(path))
    save_conversation(tid2, [{"role": "assistant", "content": "outra coisa"}], title="outro", db_path=str(path))

    # search by title
    res = search_conversations("sauda", db_path=str(path))
    assert (tid1, "saudações") in res and (tid2, "outro") not in res

    # search by message content
    res = search_conversations("outra", db_path=str(path))
    assert (tid2, "outro") in res and (tid1, "saudações") not in res

