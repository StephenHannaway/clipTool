from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ClipboardEntry:
    id: int
    content: str
    content_type: str
    raw: bytes | None
    timestamp: datetime
    pinned: bool


_URL_RE = re.compile(r"^https?://\S+$", re.IGNORECASE)
_EMAIL_RE = re.compile(r"^[\w.+\-]+@[\w\-]+\.[\w.]+$")
_CODE_RE = re.compile(r"\b(def |class |import |from |const |function |return |=>)\b")


def detect_content_type(text: str) -> str:
    s = text.strip()
    if _URL_RE.match(s):
        return "url"
    if _EMAIL_RE.match(s):
        return "email"
    if _CODE_RE.search(s):
        return "code"
    return "text"
