"""Strip a byte-order mark or decode the text behind it."""

from __future__ import annotations

from collections.abc import Iterable

from ._table import BomInfo, detect
from ._utf7 import strip_utf7


class UnsupportedBomError(LookupError):
    """The mark names an encoding Python has no codec for (UTF-1, UTF-EBCDIC, SCSU, BOCU-1)."""

    def __init__(self, encoding: str) -> None:
        super().__init__(f"the byte-order mark names {encoding}, which Python cannot decode")
        self.encoding = encoding


def codec_for(info: BomInfo) -> str:
    codec = info.codec
    if codec is None:
        raise UnsupportedBomError(info.encoding)
    return codec


def strip(data: bytes, *, among: Iterable[str] | None = None) -> bytes:
    """Return ``data`` without its leading byte-order mark, unchanged if it has none.

    Only one mark is removed. ``among`` limits which marks count, as in `detect`.
    """
    info = detect(data, among=among)
    if info is None:
        return data
    if info.encoding == "utf-7":
        return strip_utf7(data)
    return data[info.length :]


def decode(
    data: bytes,
    default: str = "utf-8",
    *,
    errors: str = "strict",
    among: Iterable[str] | None = None,
) -> str:
    """Decode ``data`` with the encoding its byte-order mark implies, else ``default``.

    The mark is consumed, never left in the returned text; a second mark is kept as
    U+FEFF. ``errors`` is passed to the codec. Raises `UnsupportedBomError` when the mark
    names an encoding Python cannot decode.
    """
    info = detect(data, among=among)
    if info is None:
        return data.decode(default, errors)
    # Decoding the mark with the rest keeps UTF-7 exact, where it shares a byte.
    text = data.decode(codec_for(info), errors)
    return text[1:] if text.startswith("\ufeff") else text
