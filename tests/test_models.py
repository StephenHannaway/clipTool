from datetime import datetime

from clipboard_manager.models import ClipboardEntry, detect_content_type


def test_clipboard_entry_fields():
    e = ClipboardEntry(
        id=1,
        content="hi",
        content_type="text",
        raw=None,
        timestamp=datetime.now(),
        pinned=False,
    )
    assert e.content == "hi"
    assert not e.pinned


def test_detect_url():
    assert detect_content_type("https://github.com/foo/bar") == "url"


def test_detect_url_http():
    assert detect_content_type("http://example.com") == "url"


def test_detect_email():
    assert detect_content_type("user@example.com") == "email"


def test_detect_email_complex():
    assert detect_content_type("first.last+tag@sub.domain.com") == "email"


def test_detect_code_python():
    assert detect_content_type("def hello():\n    return 'world'") == "code"


def test_detect_code_import():
    assert detect_content_type("import os\nfrom pathlib import Path") == "code"


def test_detect_code_js():
    assert detect_content_type("const x = () => { return 1; }") == "code"


def test_detect_text_default():
    assert detect_content_type("just a plain sentence") == "text"


def test_detect_text_short():
    assert detect_content_type("hello") == "text"


def test_detect_strips_whitespace():
    assert detect_content_type("  https://example.com  ") == "url"
