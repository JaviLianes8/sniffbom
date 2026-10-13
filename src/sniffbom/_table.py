"""The signature table: which leading bytes name which encoding scheme."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import TypeAlias

# Anything with the buffer protocol a caller is likely to hold.
BytesLike: TypeAlias = bytes | bytearray | memoryview

# Ordered longest first on purpose: a UTF-32-LE mark (FF FE 00 00) begins with the
# UTF-16-LE mark (FF FE), so the four-byte marks must be tested before the two-byte ones.
# The codec is the Python codec that reads the scheme, None when Python has none.
_MARKS: tuple[tuple[bytes, str, str | None], ...] = (
    (b"\xff\xfe\x00\x00", "utf-32-le", "utf-32-le"),
    (b"\x00\x00\xfe\xff", "utf-32-be", "utf-32-be"),
    (b"\x84\x31\x95\x33", "gb18030", "gb18030"),
    (b"\xdd\x73\x66\x73", "utf-ebcdic", None),
    (b"+/v8-", "utf-7", "utf-7"),
    (b"+/v8", "utf-7", "utf-7"),
    (b"+/v9", "utf-7", "utf-7"),
    (b"+/v+", "utf-7", "utf-7"),
    (b"+/v/", "utf-7", "utf-7"),
    (b"\xef\xbb\xbf", "utf-8", "utf-8"),
    (b"\xf7\x64\x4c", "utf-1", None),
    (b"\x0e\xfe\xff", "scsu", None),
    (b"\xfb\xee\x28", "bocu-1", None),
    (b"\xff\xfe", "utf-16-le", "utf-16-le"),
    (b"\xfe\xff", "utf-16-be", "utf-16-be"),
)

LONGEST = max(len(mark) for mark, _, _ in _MARKS)
_CODECS: dict[str, str | None] = {name: codec for _, name, codec in _MARKS}

ENCODINGS: tuple[str, ...] = tuple(dict.fromkeys(name for _, name, _ in _MARKS))
"""Every encoding name `detect` can report, in the order the marks are tried."""


@dataclass(frozen=True)
class BomInfo:
    """A detected byte-order mark: the encoding it implies and its length in bytes.

    For UTF-7 the fourth byte of the mark also carries two bits of the next character
    unless the mark is ``+/v8-``, so slicing ``data[length:]`` is only exact for that
    form; `strip` handles every form.
    """

    encoding: str
    length: int

    @property
    def codec(self) -> str | None:
        """The Python codec that reads this encoding, or ``None`` if Python has none."""
        return _CODECS.get(self.encoding)


def _marks(among: Iterable[str] | None) -> tuple[tuple[bytes, str, str | None], ...]:
    if among is None:
        return _MARKS
    if isinstance(among, (str, bytes)):
        raise TypeError("among must be a collection of encoding names, not a single string")
    wanted = set(among)
    unknown = sorted(wanted - set(ENCODINGS))
    if unknown:
        raise ValueError(f"unknown encoding names: {', '.join(unknown)}; known: {ENCODINGS}")
    return tuple(entry for entry in _MARKS if entry[1] in wanted)


def detect(data: BytesLike, *, among: Iterable[str] | None = None) -> BomInfo | None:
    """Return the byte-order mark at the start of ``data``, or ``None`` if there is none.

    ``among`` limits the search to some names of `ENCODINGS`; pass
    ``("utf-8", "utf-16-le", "utf-16-be")`` to read ``FF FE 00 00`` as UTF-16LE followed
    by NUL, the way the WHATWG Encoding Standard does, instead of as UTF-32LE.
    """
    head = bytes(data[:LONGEST])
    for mark, encoding, _ in _marks(among):
        if head.startswith(mark):
            return BomInfo(encoding=encoding, length=len(mark))
    return None


def needs_more(data: BytesLike, *, among: Iterable[str] | None = None) -> bool:
    """Return whether more bytes after ``data`` could change what `detect` returns.

    ``FF FE`` needs more (it may become UTF-32LE), ``FF FE 41`` does not. A stream reader
    keeps reading until this is false or the stream ends, then calls `detect`.
    """
    head = bytes(data[:LONGEST])
    return any(len(head) < len(mark) and mark.startswith(head) for mark, _, _ in _marks(among))
