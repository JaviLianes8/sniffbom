"""The WHATWG Encoding Standard view: "BOM sniff" and "decode"."""

from __future__ import annotations

from typing import Literal

from ._buffer import BytesLike, byte_data, byte_head
from ._codec import validate_codec

WhatwgEncoding = Literal["UTF-8", "UTF-16BE", "UTF-16LE"]
"""The three names returned by the WHATWG BOM sniff algorithm.

>>> from typing import get_args
>>> from sniffbom import WhatwgEncoding
>>> get_args(WhatwgEncoding)
('UTF-8', 'UTF-16BE', 'UTF-16LE')
"""

# The table of the "BOM sniff" algorithm, tried top to bottom, with the Python codec and
# the number of bytes "decode" skips for each row. UTF-32 is deliberately absent.
_SNIFF: tuple[tuple[bytes, WhatwgEncoding, str], ...] = (
    (b"\xef\xbb\xbf", "UTF-8", "utf-8"),
    (b"\xfe\xff", "UTF-16BE", "utf-16-be"),
    (b"\xff\xfe", "UTF-16LE", "utf-16-le"),
)


def bom_sniff(data: BytesLike) -> WhatwgEncoding | None:
    r"""Return the encoding the WHATWG "BOM sniff" algorithm reads from ``data``, or ``None``.

    Only UTF-8 and the two UTF-16 marks count, so ``FF FE 00 00`` is ``"UTF-16LE"``.

    >>> from sniffbom import bom_sniff
    >>> bom_sniff(b"\xff\xfe\x00\x00")
    'UTF-16LE'
    """
    head = byte_head(data, 3)
    for mark, name, _ in _SNIFF:
        if head.startswith(mark):
            return name
    return None


def whatwg_decode(data: BytesLike, fallback: str = "utf-8") -> str:
    r"""Decode ``data`` the way the WHATWG "decode" algorithm does.

    A mark found by `bom_sniff` wins over ``fallback`` (a Python codec name) and is
    skipped. Malformed UTF-8/16 becomes U+FFFD. Fallbacks must support replacement;
    IDNA and the undefined codec raise a bounded `LookupError`. Other codec exceptions
    propagate, including `UnicodeError` from built-in codecs.

    >>> from sniffbom import whatwg_decode
    >>> whatwg_decode(b"\xef\xbb\xbfa\xff") == "a\ufffd"
    True
    """
    data = byte_data(data)
    for mark, _, codec in _SNIFF:
        if data.startswith(mark):
            return data[len(mark) :].decode(codec, "replace")
    codec, errors, _ = validate_codec(fallback, "replace")
    return data.decode(codec, errors)
