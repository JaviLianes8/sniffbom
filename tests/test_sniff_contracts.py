"""Hand-derived contracts for exact BOM lengths and literal XML byte matching."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from sniffbom import XmlGuess, bom_sniff, xml_autodetect


@pytest.mark.parametrize("buffer", [bytes, bytearray, memoryview])
@pytest.mark.parametrize(
    ("mark", "expected"), [(b"\xfe\xff", "UTF-16BE"), (b"\xff\xfe", "UTF-16LE")]
)
def test_bom_sniff_accepts_complete_utf16_marks_without_payload(
    buffer: Callable[[bytes], bytes | bytearray | memoryview], mark: bytes, expected: str
) -> None:
    assert bom_sniff(buffer(mark)) == expected


@pytest.mark.parametrize("buffer", [bytes, bytearray, memoryview])
@pytest.mark.parametrize("prefix", [b"\xfe", b"\xff", b"\xef"])
def test_bom_sniff_rejects_single_byte_prefixes(
    buffer: Callable[[bytes], bytes | bytearray | memoryview], prefix: bytes
) -> None:
    assert bom_sniff(buffer(prefix)) is None


@pytest.mark.parametrize("buffer", [bytes, bytearray, memoryview])
@pytest.mark.parametrize("whitespace", [b" ", b"\t", b"\n", b"\r", b"\v", b"\f"])
@pytest.mark.parametrize(
    "mark",
    [
        b"\x00\x00\xfe\xff",
        b"\xff\xfe\x00\x00",
        b"\x00\x00\xff\xfe",
        b"\xfe\xff\x00\x00",
        b"\xfe\xff",
        b"\xff\xfe",
        b"\xef\xbb\xbf",
    ],
)
def test_xml_autodetect_rejects_whitespace_prefixed_marks(
    buffer: Callable[[bytes], bytes | bytearray | memoryview], whitespace: bytes, mark: bytes
) -> None:
    assert xml_autodetect(buffer(whitespace + mark)) == XmlGuess("other", 0, "utf-8")


@pytest.mark.parametrize("buffer", [bytes, bytearray, memoryview])
@pytest.mark.parametrize(
    "signature",
    [b"<?XM", b"<?Xm", b"<?xM", b"\x6c\x6f\xa7\x94", b"\x4c\x4f\xa7\x94", b"\x6c\x4f\xa7\x94"],
)
def test_xml_autodetect_requires_literal_signature_case(
    buffer: Callable[[bytes], bytes | bytearray | memoryview], signature: bytes
) -> None:
    # Include ASCII case folding of the EBCDIC row's raw bytes, not its decoded text.
    assert xml_autodetect(buffer(signature)) == XmlGuess("other", 0, "utf-8")
