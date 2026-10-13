"""UTF-7 marks: the fourth byte carries two bits of the next character (RFC 2152)."""

from __future__ import annotations

import pytest

from sniffbom import decode, detect, strip

SAMPLES = [
    *[chr(code) for code in range(0x20, 0x7F)],
    "\t",
    "\n",
    "\xe9",
    "中",
    "耀",
    "쀀",
    "￿",
    "\U0001f600",
    "ab",
    "\xe9\xe9",
    "\xe9a中-",
    "+",
    "+-",
    "\U0001f600x\U0001f600",
    "",
]


def _marked(text: str) -> bytes:
    return ("﻿" + text).encode("utf-7")


@pytest.mark.parametrize("text", SAMPLES)
def test_strip_keeps_the_text_after_the_mark(text: str) -> None:
    data = _marked(text)
    assert detect(data) is not None and detect(data).encoding == "utf-7"  # type: ignore[union-attr]
    stripped = strip(data)
    assert stripped.decode("utf-7") == text
    assert decode(data) == text


@pytest.mark.parametrize(
    ("text", "fourth"), [("A", b"8"), ("中", b"9"), ("耀", b"+"), ("쀀", b"/")]
)
def test_the_fourth_byte_follows_the_next_character(text: str, fourth: bytes) -> None:
    assert _marked(text)[:4] == b"+/v" + fourth
    assert strip(_marked(text)).decode("utf-7") == text


def test_a_mark_that_ends_its_run_is_cut_with_the_terminator() -> None:
    assert strip(b"+/v8-A") == b"A"
    assert strip(b"+/v8!") == b"!"
    assert strip(b"+/v8") == b""
    assert strip(b"+/v8-") == b""


def test_the_rest_of_the_run_is_re_encoded() -> None:
    assert strip(b"+/v8A6Q-") == b"+AOk-"
    assert strip(b"+/v8A6Q") == b"+AOk"
    assert strip(b"+/v8A6Q x") == b"+AOk x"


def test_a_minus_after_a_re_encoded_run_is_kept() -> None:
    # "+AOk-" followed by a literal "-" written as "--" stays decodable.
    data = _marked("\xe9-")
    assert strip(data).decode("utf-7") == "\xe9-"


def test_a_run_with_stray_bits_is_left_unchanged() -> None:
    assert strip(b"+/v9") == b"+/v9"
    assert strip(b"+/v9-x") == b"+/v9-x"


def test_a_plus_minus_literal_is_not_a_mark() -> None:
    assert detect(b"+-/v8") is None
