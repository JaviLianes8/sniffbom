"""Autodetection of an XML entity's encoding family, after XML 1.0 Appendix F.1."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

XmlFamily = Literal[
    "ucs-4-1234",
    "ucs-4-4321",
    "ucs-4-2143",
    "ucs-4-3412",
    "utf-16-be",
    "utf-16-le",
    "utf-8",
    "ascii",
    "ebcdic",
    "other",
]


@dataclass(frozen=True)
class XmlGuess:
    """What the first bytes of an XML entity say about its encoding.

    ``family`` names the row of Appendix F.1 that matched, ``bom_length`` is the length of
    the mark (0 without one) and ``codec`` is the Python codec when the family alone
    decides it, ``None`` when the encoding declaration must be read to choose.
    """

    family: XmlFamily
    bom_length: int
    codec: str | None


# Rows of the table, tried in this order. "FE FF ## ##" and "FF FE ## ##" (UTF-16 with a
# mark) come after the UCS-4 rows they would otherwise shadow.
_WITH_MARK: tuple[tuple[bytes, XmlFamily, str | None], ...] = (
    (b"\x00\x00\xfe\xff", "ucs-4-1234", "utf-32-be"),
    (b"\xff\xfe\x00\x00", "ucs-4-4321", "utf-32-le"),
    (b"\x00\x00\xff\xfe", "ucs-4-2143", None),
    (b"\xfe\xff\x00\x00", "ucs-4-3412", None),
    (b"\xfe\xff", "utf-16-be", "utf-16-be"),
    (b"\xff\xfe", "utf-16-le", "utf-16-le"),
    (b"\xef\xbb\xbf", "utf-8", "utf-8"),
)
_WITHOUT_MARK: tuple[tuple[bytes, XmlFamily], ...] = (
    (b"\x00\x00\x00\x3c", "ucs-4-1234"),
    (b"\x3c\x00\x00\x00", "ucs-4-4321"),
    (b"\x00\x00\x3c\x00", "ucs-4-2143"),
    (b"\x00\x3c\x00\x00", "ucs-4-3412"),
    (b"\x00\x3c\x00\x3f", "utf-16-be"),
    (b"\x3c\x00\x3f\x00", "utf-16-le"),
    (b"\x3c\x3f\x78\x6d", "ascii"),
    (b"\x4c\x6f\xa7\x94", "ebcdic"),
)


def xml_autodetect(data: bytes) -> XmlGuess:
    """Name the encoding family of an XML entity from its first four bytes.

    Input shorter than four bytes is taken as the whole entity. Anything that matches no
    row is ``"other"``: UTF-8 without a declaration, unless the entity is mislabelled.
    """
    for mark, family, codec in _WITH_MARK:
        if data.startswith(mark):
            return XmlGuess(family, len(mark), codec)
    for prefix, family in _WITHOUT_MARK:
        if data.startswith(prefix):
            return XmlGuess(family, 0, None)
    return XmlGuess("other", 0, "utf-8")
