import sys
import types
import pytest
import pathlib

# Stub external dependencies used during import
sys.modules['requests'] = types.ModuleType('requests')
dummy_token_manager = types.ModuleType('token_manager')
class DummyTokenManager:  # pragma: no cover - minimal stub
    pass
dummy_token_manager.TokenManager = DummyTokenManager
sys.modules['token_manager'] = dummy_token_manager

# Ensure repository root is on sys.path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from mail import format_body


def test_strip_tags():
    html = "<p>Hello <b>World</b></p>"
    assert format_body(html) == "Hello World"


def test_convert_links_to_markdown():
    html = "<p>See <a href='https://example.com'>example</a></p>"
    assert format_body(html) == "See [example](https://example.com)"

