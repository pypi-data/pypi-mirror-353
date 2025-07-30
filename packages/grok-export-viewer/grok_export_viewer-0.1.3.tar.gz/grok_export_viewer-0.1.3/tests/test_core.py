import pytest
from pathlib import Path
from grok_export_viewer.core import sessions, clean, rows, export_markdown

def test_clean():
    assert clean("Test /:* Title") == "Test_Title"
    assert len(clean("x" * 200)) <= 100

def test_sessions_invalid_file(tmp_path):
    invalid_file = tmp_path / "invalid.json"
    invalid_file.write_text("not json")
    with pytest.raises(ValueError, match="Failed to load JSON file"):
        sessions(invalid_file)

def test_sessions_invalid_format(tmp_path):
    invalid_file = tmp_path / "invalid.json"
    invalid_file.write_text('{"not_conversations": []}')
    with pytest.raises(ValueError, match="Invalid JSON format: 'conversations' must be a list"):
        sessions(invalid_file)

def test_rows():
    item = {
        "conversation": {"title": "Test Chat"},
        "responses": [
            {"response": {"sender": "user", "message": "Hello"}},
            {"response": {"sender": "grok", "message": "Hi!"}},
        ]
    }
    title, msgs = rows(item, 1)
    assert title == "Test Chat"
    assert len(msgs) == 2
    assert msgs[0] == {"sender": "user", "text": "Hello"}
    assert msgs[1] == {"sender": "grok", "text": "Hi!"}

def test_export_markdown(tmp_path):
    conv = [{
        "conversation": {"title": "Test Chat"},
        "responses": [
            {"response": {"sender": "user", "message": "Hello"}},
        ]
    }]
    out = export_markdown(conv, output_dir=tmp_path / "markdown")
    md_file = out / "001_Test_Chat.md"
    assert md_file.exists()
    assert "Hello" in md_file.read_text()