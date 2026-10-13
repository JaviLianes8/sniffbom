"""The WHATWG decode view and XML 1.0 Appendix F.1 (tables restated by hand here, read
back from the pinned specifications in tests/test_sources.py)."""

from __future__ import annotations

import pytest

from sniffbom import XmlGuess, bom_sniff, whatwg_decode, xml_autodetect


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (b"\xef\xbb\xbfx", "UTF-8"),
        (b"\xfe\xff\x00x", "UTF-16BE"),
        (b"\xff\xfex\x00", "UTF-16LE"),
        (b"\xff\xfe\x00\x00", "UTF-16LE"),
        (b"\x00\x00\xfe\xff", None),
        (b"\x84\x31\x95\x33", None),
        (b"\xef\xbb", None),
        (b"", None),
    ],
)
def test_bom_sniff_reads_only_the_three_rows(data: bytes, expected: str | None) -> None:
    assert bom_sniff(data) == expected


def test_whatwg_decode_lets_the_mark_win_over_the_fallback() -> None:
    assert whatwg_decode(b"\xfe\xff\x00h\x00i", "latin-1") == "hi"
    assert whatwg_decode(b"\xef\xbb\xbfh\xc3\xa9", "utf-16-le") == "h\xe9"


def test_whatwg_decode_uses_the_fallback_without_a_mark() -> None:
    assert whatwg_decode(b"caf\xe9", "latin-1") == "caf\xe9"
    assert whatwg_decode(b"caf\xc3\xa9") == "caf\xe9"


def test_whatwg_decode_skips_exactly_one_mark() -> None:
    assert whatwg_decode(b"\xef\xbb\xbf\xef\xbb\xbfx") == "\ufeffx"


def test_whatwg_decode_reads_ff_fe_00_00_as_utf16_le_nul() -> None:
    assert whatwg_decode(b"\xff\xfe\x00\x00") == "\x00"


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (b"a\xffb", "a\ufffdb"),
        (b"\xc3", "\ufffd"),
        (b"\xfe\xff\x00", "\ufffd"),
        (b"\xff\xfe\x00\xd8A\x00", "\ufffdA"),
    ],
)
def test_whatwg_decode_replaces_errors(data: bytes, expected: str) -> None:
    # Hand-derived from the UTF-8 and UTF-16 decoders of the standard, not copied.
    assert whatwg_decode(data) == expected


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (b"\x00\x00\xfe\xff", XmlGuess("ucs-4-1234", 4, "utf-32-be")),
        (b"\xff\xfe\x00\x00", XmlGuess("ucs-4-4321", 4, "utf-32-le")),
        (b"\x00\x00\xff\xfe", XmlGuess("ucs-4-2143", 4, None)),
        (b"\xfe\xff\x00\x00", XmlGuess("ucs-4-3412", 4, None)),
        (b"\xfe\xff\x00<", XmlGuess("utf-16-be", 2, "utf-16-be")),
        (b"\xff\xfe<\x00", XmlGuess("utf-16-le", 2, "utf-16-le")),
        (b"\xef\xbb\xbf<?xm", XmlGuess("utf-8", 3, "utf-8")),
        (b"\x00\x00\x00<", XmlGuess("ucs-4-1234", 0, None)),
        (b"<\x00\x00\x00", XmlGuess("ucs-4-4321", 0, None)),
        (b"\x00\x00<\x00", XmlGuess("ucs-4-2143", 0, None)),
        (b"\x00<\x00\x00", XmlGuess("ucs-4-3412", 0, None)),
        (b"\x00<\x00?", XmlGuess("utf-16-be", 0, None)),
        (b"<\x00?\x00", XmlGuess("utf-16-le", 0, None)),
        (b"<?xml version", XmlGuess("ascii", 0, None)),
        (b"\x4c\x6f\xa7\x94", XmlGuess("ebcdic", 0, None)),
        (b"<root/>", XmlGuess("other", 0, "utf-8")),
        (b"", XmlGuess("other", 0, "utf-8")),
    ],
)
def test_xml_autodetect_follows_appendix_f(data: bytes, expected: XmlGuess) -> None:
    assert xml_autodetect(data) == expected


def test_xml_short_input_is_taken_as_the_whole_entity() -> None:
    # "FE FF 00" cannot become "FE FF 00 00" any more, so it is UTF-16 with a mark.
    assert xml_autodetect(b"\xfe\xff\x00") == XmlGuess("utf-16-be", 2, "utf-16-be")
    assert xml_autodetect(b"\xfe\xff") == XmlGuess("utf-16-be", 2, "utf-16-be")


def test_xml_codec_decodes_the_entity() -> None:
    entity = "\ufeff<?xml version='1.0'?><a>\xe9</a>"
    for codec in ("utf-16-le", "utf-16-be", "utf-32-le", "utf-32-be", "utf-8"):
        data = entity.encode(codec)
        guess = xml_autodetect(data)
        assert guess.codec == codec
        assert data[guess.bom_length :].decode(codec) == entity[1:]
