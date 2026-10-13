"""Every table value is read back from the pinned sources (see tests/upstream/MANIFEST.json).

The tests skip until `python scripts/fetch_upstream.py` has fetched the files.
"""

from __future__ import annotations

import re

import pytest
from conftest import hex_bytes, page_text, read_upstream

from sniffbom import ENCODINGS, XmlGuess, bom_sniff, detect, whatwg_decode, xml_autodetect
from sniffbom._whatwg import _SNIFF
from sniffbom._xml import _WITH_MARK, _WITHOUT_MARK

HEX = r"((?:[0-9A-F]{2} )+[0-9A-F]{2})\b"


def _after(text: str, start: str, end: str) -> str:
    section = text.split(start, 1)[1]
    return section.split(end, 1)[0]


def test_the_unicode_faq_table() -> None:
    table = _after(page_text("faq-utf-bom.html"), "Bytes Encoding Form", "Q:")
    rows = re.findall(HEX + r" UTF-(8|16|32)(?:, (big|little)-endian)?", table)
    assert len(rows) == 5
    for mark, bits, order in rows:
        name = f"utf-{bits}" + ({"big": "-be", "little": "-le"}.get(order, ""))
        assert detect(hex_bytes(mark)) == detect(hex_bytes(mark) + b"x")
        assert detect(hex_bytes(mark) + b"x").encoding == name  # type: ignore[union-attr]
        assert detect(hex_bytes(mark) + b"x").length == len(hex_bytes(mark))  # type: ignore[union-attr]


def test_the_scsu_signature_of_uts_6() -> None:
    table = _after(page_text("uts6-scsu.html"), "Table 8. Possible Encodings", "8.2")
    preferred = re.search(r"Preferred " + HEX, table)
    assert preferred is not None
    assert detect(hex_bytes(preferred.group(1)) + b"A") == detect(b"\x0e\xfe\xffA")
    assert detect(hex_bytes(preferred.group(1))).encoding == "scsu"  # type: ignore[union-attr]


def test_the_bocu1_signature_of_utn_6() -> None:
    found = re.search(
        r"U\+FEFF is encoded in BOCU-1 with the three bytes " + HEX, page_text("utn6-bocu1.html")
    )
    assert found is not None
    assert detect(hex_bytes(found.group(1))).encoding == "bocu-1"  # type: ignore[union-attr]


def test_the_utf_ebcdic_signature_of_utr_16() -> None:
    found = re.search(r"maps to X'" + HEX + r"' in UTF-EBCDIC", page_text("utr16-utf-ebcdic.html"))
    assert found is not None
    assert detect(hex_bytes(found.group(1))).encoding == "utf-ebcdic"  # type: ignore[union-attr]


WIKIPEDIA_ROWS = {
    "UTF-8": "utf-8",
    "UTF-16 ( BE )": "utf-16-be",
    "UTF-16 ( LE )": "utf-16-le",
    "UTF-32 (BE)": "utf-32-be",
    "UTF-32 (LE)": "utf-32-le",
    "UTF-7": "utf-7",
    "UTF-1": "utf-1",
    "UTF-EBCDIC": "utf-ebcdic",
    "SCSU": "scsu",
    "BOCU-1": "bocu-1",
    "GB18030": "gb18030",
}


def test_the_wikipedia_table_covers_every_encoding() -> None:
    text = page_text("wikipedia-bom.html").split("Bytes interpreted as", 1)[1]
    assert set(WIKIPEDIA_ROWS.values()) == set(ENCODINGS)
    for label, name in WIKIPEDIA_ROWS.items():
        text = text.split(label, 1)[1]
        mark = hex_bytes(re.search(HEX, text).group(1))  # type: ignore[union-attr]
        if name == "utf-7":
            note = re.search(r"Followed by ((?:[0-9A-F]{2} ?, )+)or ([0-9A-F]{2})", text)
            assert note is not None
            fourth = hex_bytes(note.group(1).replace(",", " ") + note.group(2))
            assert mark == b"+/v" and detect(mark) is None
            for byte in fourth:
                assert detect(mark + bytes([byte])).encoding == "utf-7"  # type: ignore[union-attr]
            continue
        assert detect(mark + b"x").encoding == name, label  # type: ignore[union-attr]


def test_gb18030_mark_is_the_codec_form_of_u_feff() -> None:
    # Second, independent source for the Wikipedia value: the Python codec itself.
    assert detect("\ufeff".encode("gb18030")).encoding == "gb18030"  # type: ignore[union-attr]


def test_utf7_alphabet_is_the_one_rfc_2152_names() -> None:
    rfc = read_upstream("rfc2152.txt")
    assert "Modified Base64" in rfc and "RFC 2045" in rfc
    assert detect("\ufeff".encode("utf-7")).encoding == "utf-7"  # type: ignore[union-attr]


def test_the_whatwg_bom_sniff_table() -> None:
    section = _after(page_text("whatwg-encoding.html"), "To BOM sniff an I/O queue", "This hook")
    assert "peeking 3 bytes" in section
    rows = re.findall(r"((?:0x[0-9A-F]{2} ?)+) (UTF-\S+)", section)
    assert [(hex_bytes(mark), name) for mark, name in rows] == [(m, n) for m, n, _ in _SNIFF]
    for mark, name in rows:
        assert bom_sniff(hex_bytes(mark) + b"\x00\x00") == name


def test_the_whatwg_decode_algorithm() -> None:
    section = _after(page_text("whatwg-encoding.html"), "To decode an I/O queue", "To BOM sniff")
    assert re.search(
        r"Read three bytes from ioQueue , if BOMEncoding is UTF-8 ; otherwise read two", section
    )
    assert '" replacement "' in section
    assert whatwg_decode(b"\xef\xbb\xbf\xef\xbb\xbf") == "\ufeff"
    assert whatwg_decode(b"\xff\xfe\xff\xfe") == "\ufeff"


XML_WITH_MARK = ["1234", "4321", "2143", "3412", "UTF-16, big", "UTF-16, little", "UTF-8"]
XML_WITHOUT = ["32-bit", "", "", "", "UTF-16BE", "UTF-16LE", "ASCII", "EBCDIC"]
XmlRows = tuple[list[tuple[bytes, str]], list[tuple[bytes, str]]]


def _rows(text: str) -> list[tuple[bytes, str]]:
    token = r"(?:[0-9A-F]{2}|##)"
    parts = re.split(rf"((?:{token} ){{2,3}}{token})(?= )", text)[1:]
    # "##" is any byte, but two of them are never both 00: "41" stands for it.
    return [
        (hex_bytes(p.replace("##", "41")), d.strip())
        for p, d in zip(parts[::2], parts[1::2], strict=True)
    ]


@pytest.fixture(scope="module")
def appendix_f() -> XmlRows:
    text = _after(page_text("xml.html"), "With a Byte Order Mark:", "This level of autodetection")
    marked, unmarked = text.split("Without a Byte Order Mark:")
    return _rows(marked), _rows(unmarked.split(" Other ")[0])


def test_the_xml_rows_with_a_mark(appendix_f: XmlRows) -> None:
    rows = appendix_f[0]
    assert len(rows) == len(_WITH_MARK) == len(XML_WITH_MARK)
    for (sample, description), keyword, entry in zip(rows, XML_WITH_MARK, _WITH_MARK, strict=True):
        assert keyword in description, description
        assert sample.startswith(entry[0])
        assert xml_autodetect(sample) == XmlGuess(entry[1], len(entry[0]), entry[2])


def test_the_xml_rows_without_a_mark(appendix_f: XmlRows) -> None:
    rows = appendix_f[1]
    assert [sample for sample, _ in rows] == [prefix for prefix, _ in _WITHOUT_MARK]
    for (sample, description), keyword in zip(rows, XML_WITHOUT, strict=True):
        assert keyword in description, description
        assert xml_autodetect(sample).bom_length == 0
    # The four 32-bit rows share one description that names their orders in sequence.
    orders = re.findall(r"\((\d{4})(?:\)| and (\d{4})\))", rows[0][1])
    named = [order for pair in orders for order in pair if order]
    assert named == ["1234", "4321", "2143", "3412"]
    assert [family for _, family in _WITHOUT_MARK[:4]] == [f"ucs-4-{o}" for o in named]
