"""Detect, name and strip the Unicode byte-order mark on a byte string."""

from __future__ import annotations

from ._bom import UnsupportedBomError, decode, strip
from ._stream import text_stream
from ._table import ENCODINGS, BomInfo, detect, needs_more
from ._whatwg import WhatwgEncoding, bom_sniff, whatwg_decode
from ._xml import XmlFamily, XmlGuess, xml_autodetect

__version__ = "1.0.0"

BomInfo.__module__ = __name__
XmlGuess.__module__ = __name__
UnsupportedBomError.__module__ = __name__

del annotations

__all__ = [
    "ENCODINGS",
    "BomInfo",
    "UnsupportedBomError",
    "WhatwgEncoding",
    "XmlFamily",
    "XmlGuess",
    "bom_sniff",
    "decode",
    "detect",
    "needs_more",
    "strip",
    "text_stream",
    "whatwg_decode",
    "xml_autodetect",
]
