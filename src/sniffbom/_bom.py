"""Detect, name and strip the Unicode byte-order mark on a byte string."""

from __future__ import annotations

from dataclasses import dataclass

# Ordered longest first on purpose: a UTF-32-LE mark (FF FE 00 00) begins with the
# UTF-16-LE mark (FF FE), so the four-byte marks must be tested before the two-byte ones.
_MARKS: tuple[tuple[bytes, str], ...] = (
    (b"\xff\xfe\x00\x00", "utf-32-le"),
    (b"\x00\x00\xfe\xff", "utf-32-be"),
    (b"\xef\xbb\xbf", "utf-8"),
    (b"\xff\xfe", "utf-16-le"),
    (b"\xfe\xff", "utf-16-be"),
)


@dataclass(frozen=True)
class BomInfo:
    """A detected byte-order mark: the encoding it implies and its length in bytes."""

    encoding: str
    length: int


def detect(data: bytes) -> BomInfo | None:
    """Return the byte-order mark at the start of ``data``, or ``None`` if there is none."""
    for mark, encoding in _MARKS:
        if data.startswith(mark):
            return BomInfo(encoding=encoding, length=len(mark))
    return None


def strip(data: bytes) -> bytes:
    """Return ``data`` without its leading byte-order mark, unchanged if it has none."""
    info = detect(data)
    return data[info.length :] if info else data


def decode(data: bytes, default: str = "utf-8") -> str:
    """Decode ``data`` with the encoding its byte-order mark implies, else ``default``.

    The mark is consumed, never left in the returned text.
    """
    info = detect(data)
    if info is None:
        return data.decode(default)
    return data[info.length :].decode(info.encoding)
