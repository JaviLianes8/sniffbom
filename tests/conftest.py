from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path

import pytest

UPSTREAM = Path(__file__).resolve().parent / "upstream"


def read_upstream(name: str) -> str:
    """Return a third-party reference file as text.

    The files are not committed: `python scripts/fetch_upstream.py` fetches them. Their
    tests skip while a file is absent and fail if it differs from the manifest.
    """
    path = UPSTREAM / name
    if not path.is_file():
        pytest.skip(f"{name} is not fetched; run python scripts/fetch_upstream.py")
    entry = json.loads((UPSTREAM / "MANIFEST.json").read_text(encoding="utf-8"))[name]
    body = path.read_bytes()
    assert hashlib.sha256(body).hexdigest() == entry["sha256"], f"{name} differs from MANIFEST"
    return body.decode("utf-8")


def page_text(name: str) -> str:
    """An HTML reference page as plain text: tags dropped, entities read, spaces folded."""
    text = re.sub(r"<(script|style)\b.*?</\1>", " ", read_upstream(name), flags=re.S | re.I)
    text = html.unescape(re.sub(r"<[^>]+>", " ", text))
    return re.sub(r"\s+", " ", text)


def hex_bytes(text: str) -> bytes:
    """``"EF BB BF"`` or ``"0xEF 0xBB 0xBF"`` as bytes."""
    return bytes(int(part, 16) for part in text.replace("0x", " ").split())
