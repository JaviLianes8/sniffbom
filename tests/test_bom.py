import codecs

import pytest

from sniffbom import BomInfo, decode, detect, strip

CASES = [
    (codecs.BOM_UTF8, "utf-8", 3),
    (codecs.BOM_UTF16_LE, "utf-16-le", 2),
    (codecs.BOM_UTF16_BE, "utf-16-be", 2),
    (codecs.BOM_UTF32_LE, "utf-32-le", 4),
    (codecs.BOM_UTF32_BE, "utf-32-be", 4),
]


@pytest.mark.parametrize(("mark", "encoding", "length"), CASES)
def test_each_bom_is_detected_with_name_and_length(mark: bytes, encoding: str, length: int) -> None:
    assert detect(mark + b"hi") == BomInfo(encoding=encoding, length=length)


def test_utf32_le_is_not_misread_as_utf16_le() -> None:
    # UTF-32-LE starts with the UTF-16-LE mark, so order of checks matters.
    info = detect(codecs.BOM_UTF32_LE + b"\x00\x00\x00\x00")
    assert info == BomInfo(encoding="utf-32-le", length=4)


def test_bare_utf16_le_stays_utf16_le() -> None:
    assert detect(codecs.BOM_UTF16_LE + b"a\x00") == BomInfo(encoding="utf-16-le", length=2)


def test_no_bom_returns_none() -> None:
    assert detect(b"plain text") is None


def test_empty_input_returns_none() -> None:
    assert detect(b"") is None


def test_short_input_returns_none() -> None:
    assert detect(b"\xef") is None
    assert detect(b"\xff") is None


def test_strip_removes_only_the_bom() -> None:
    assert strip(codecs.BOM_UTF8 + b"hello") == b"hello"


def test_strip_leaves_unmarked_bytes_untouched() -> None:
    assert strip(b"hello") == b"hello"


def test_strip_empty_is_empty() -> None:
    assert strip(b"") == b""


ROUND_TRIP = [
    (codecs.BOM_UTF8, "utf-8"),
    (codecs.BOM_UTF16_LE, "utf-16-le"),
    (codecs.BOM_UTF16_BE, "utf-16-be"),
    (codecs.BOM_UTF32_LE, "utf-32-le"),
    (codecs.BOM_UTF32_BE, "utf-32-be"),
]


@pytest.mark.parametrize(("mark", "encoding"), ROUND_TRIP)
def test_decode_round_trip(mark: bytes, encoding: str) -> None:
    text = "café ñ \U0001f600"
    assert decode(mark + text.encode(encoding)) == text


def test_decode_without_bom_uses_default_utf8() -> None:
    assert decode(b"plain") == "plain"


def test_decode_honours_explicit_default() -> None:
    assert decode(b"\xe9", default="latin-1") == "é"
