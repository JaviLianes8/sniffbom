"""The WHATWG Encoding Standard view: "BOM sniff" and "decode"."""

from __future__ import annotations

from typing import Literal

WhatwgEncoding = Literal["UTF-8", "UTF-16BE", "UTF-16LE"]

# The table of the "BOM sniff" algorithm, tried top to bottom, with the Python codec and
# the number of bytes "decode" skips for each row. UTF-32 is deliberately absent.
_SNIFF: tuple[tuple[bytes, WhatwgEncoding, str], ...] = (
    (b"\xef\xbb\xbf", "UTF-8", "utf-8"),
    (b"\xfe\xff", "UTF-16BE", "utf-16-be"),
    (b"\xff\xfe", "UTF-16LE", "utf-16-le"),
)


def bom_sniff(data: bytes) -> WhatwgEncoding | None:
    """Return the encoding the WHATWG "BOM sniff" algorithm reads from ``data``, or ``None``.

    Only UTF-8 and the two UTF-16 marks count, so ``FF FE 00 00`` is ``"UTF-16LE"``.
    """
    for mark, name, _ in _SNIFF:
        if data.startswith(mark):
            return name
    return None


def whatwg_decode(data: bytes, fallback: str = "utf-8") -> str:
    """Decode ``data`` the way the WHATWG "decode" algorithm does.

    A mark found by `bom_sniff` wins over ``fallback`` (a Python codec name) and is
    skipped; anything malformed becomes U+FFFD instead of raising.
    """
    for mark, _, codec in _SNIFF:
        if data.startswith(mark):
            return data[len(mark) :].decode(codec, "replace")
    return data.decode(fallback, "replace")
