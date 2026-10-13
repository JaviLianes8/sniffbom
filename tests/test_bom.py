import codecs

import pytest

from sniffbom import ENCODINGS, BomInfo, UnsupportedBomError, decode, detect, strip

# The marks below are restated by hand; tests/test_sources.py reads each one back from
# the pinned specifications.
CASES = [
    (codecs.BOM_UTF8, "utf-8", 3),
    (codecs.BOM_UTF16_LE, "utf-16-le", 2),
    (codecs.BOM_UTF16_BE, "utf-16-be", 2),
    (codecs.BOM_UTF32_LE, "utf-32-le", 4),
    (codecs.BOM_UTF32_BE, "utf-32-be", 4),
    (b"\x84\x31\x95\x33", "gb18030", 4),
    (b"\xdd\x73\x66\x73", "utf-ebcdic", 4),
    (b"\xf7\x64\x4c", "utf-1", 3),
    (b"\x0e\xfe\xff", "scsu", 3),
    (b"\xfb\xee\x28", "bocu-1", 3),
    (b"+/v8", "utf-7", 4),
    (b"+/v9", "utf-7", 4),
    (b"+/v+", "utf-7", 4),
    (b"+/v/", "utf-7", 4),
    (b"+/v8-", "utf-7", 5),
]


@pytest.mark.parametrize(("mark", "encoding", "length"), CASES)
def test_each_bom_is_detected_with_name_and_length(mark: bytes, encoding: str, length: int) -> None:
    assert detect(mark + b"hi") == BomInfo(encoding=encoding, length=length)


def test_encodings_lists_every_name_once_in_match_order() -> None:
    assert set(ENCODINGS) == {encoding for _, encoding, _ in CASES}
    assert len(ENCODINGS) == len(set(ENCODINGS)) == 11
    assert ENCODINGS.index("utf-32-le") < ENCODINGS.index("utf-16-le")


def test_utf32_le_is_not_misread_as_utf16_le() -> None:
    info = detect(codecs.BOM_UTF32_LE + b"\x00\x00\x00\x00")
    assert info == BomInfo(encoding="utf-32-le", length=4)


def test_bare_utf16_le_stays_utf16_le() -> None:
    assert detect(codecs.BOM_UTF16_LE + b"a\x00") == BomInfo(encoding="utf-16-le", length=2)


def test_among_reads_ff_fe_00_00_as_utf16_le() -> None:
    web = ("utf-8", "utf-16-le", "utf-16-be")
    assert detect(b"\xff\xfe\x00\x00", among=web) == BomInfo("utf-16-le", 2)
    assert decode(b"\xff\xfe\x00\x00A\x00", among=web) == "\x00A"


def test_among_ignores_marks_outside_the_set() -> None:
    assert detect(codecs.BOM_UTF8 + b"x", among=["utf-16-le"]) is None
    assert detect(codecs.BOM_UTF8 + b"x", among=()) is None


def test_among_rejects_unknown_names() -> None:
    with pytest.raises(ValueError, match="utf16le"):
        detect(b"", among=["utf16le"])


def test_among_rejects_a_bare_string() -> None:
    with pytest.raises(TypeError):
        detect(b"", among="utf-8")


def test_utf7_needs_a_valid_fourth_byte() -> None:
    assert detect(b"+/vA") is None
    assert detect(b"+/v") is None


@pytest.mark.parametrize(
    ("encoding", "codec"),
    [("utf-8", "utf-8"), ("gb18030", "gb18030"), ("utf-7", "utf-7"), ("scsu", None)],
)
def test_bominfo_names_its_python_codec(encoding: str, codec: str | None) -> None:
    assert BomInfo(encoding, 3).codec == codec


def test_no_bom_returns_none() -> None:
    assert detect(b"plain text") is None


def test_empty_input_returns_none() -> None:
    assert detect(b"") is None


def test_short_input_returns_none() -> None:
    assert detect(b"\xef") is None
    assert detect(b"\xff") is None


def test_strip_removes_only_the_bom() -> None:
    assert strip(codecs.BOM_UTF8 + b"hello") == b"hello"


def test_strip_removes_only_one_mark() -> None:
    assert strip(codecs.BOM_UTF8 * 2 + b"x") == codecs.BOM_UTF8 + b"x"


@pytest.mark.parametrize(("mark", "encoding"), [(m, e) for m, e, _ in CASES if e != "utf-7"])
def test_strip_removes_every_kind_of_mark(mark: bytes, encoding: str) -> None:
    # UTF-7 marks share bits with the next character: tests/test_utf7.py covers them.
    assert strip(mark + b"x") == b"x"


def test_strip_leaves_unmarked_bytes_untouched() -> None:
    assert strip(b"hello") == b"hello"


def test_strip_empty_is_empty() -> None:
    assert strip(b"") == b""


def test_strip_honours_among() -> None:
    assert strip(codecs.BOM_UTF8 + b"x", among=["utf-16-le"]) == codecs.BOM_UTF8 + b"x"


ROUND_TRIP = ["utf-8", "utf-16-le", "utf-16-be", "utf-32-le", "utf-32-be", "gb18030", "utf-7"]


@pytest.mark.parametrize("encoding", ROUND_TRIP)
def test_decode_round_trip(encoding: str) -> None:
    text = "café ñ \U0001f600"
    encoded = ("﻿" + text).encode(encoding)
    assert detect(encoded) is not None
    assert decode(encoded) == text


def test_decode_keeps_a_second_mark() -> None:
    assert decode(codecs.BOM_UTF8 * 2 + b"x") == "﻿x"


def test_decode_without_bom_uses_default_utf8() -> None:
    assert decode(b"plain") == "plain"


def test_decode_honours_explicit_default() -> None:
    assert decode(b"\xe9", default="latin-1") == "é"


def test_decode_passes_errors_to_the_codec() -> None:
    assert decode(codecs.BOM_UTF8 + b"a\xff", errors="replace") == "a�"
    assert decode(b"a\xff", errors="replace") == "a�"
    with pytest.raises(UnicodeDecodeError):
        decode(codecs.BOM_UTF8 + b"a\xff")


@pytest.mark.parametrize("mark", [b"\xdd\x73\x66\x73", b"\xf7\x64\x4c", b"\x0e\xfe\xff"])
def test_decode_refuses_schemes_python_cannot_read(mark: bytes) -> None:
    with pytest.raises(UnsupportedBomError) as caught:
        decode(mark + b"x")
    assert isinstance(caught.value, LookupError)
    assert caught.value.encoding == detect(mark).encoding  # type: ignore[union-attr]
    assert caught.value.encoding in str(caught.value)
