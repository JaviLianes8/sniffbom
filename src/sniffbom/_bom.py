"""Strip a byte-order mark or decode the text behind it."""

from __future__ import annotations

from collections.abc import Iterable

from ._buffer import BytesLike, byte_data
from ._codec import validate_codec
from ._table import ENCODINGS, BomInfo, detect
from ._utf7 import strip_utf7


class UnsupportedBomError(LookupError):
    r"""The mark names an encoding Python cannot decode; ``encoding`` holds its name.

    >>> from sniffbom import UnsupportedBomError, decode
    >>> try:
    ...     decode(b"\x0e\xfe\xff")
    ... except UnsupportedBomError as error:
    ...     print(error.encoding)
    scsu
    """

    def __init__(self, encoding: str) -> None:
        if not isinstance(encoding, str):
            raise TypeError("encoding must be a string")
        encoding = str.__str__(encoding)
        name = next((name for name in ENCODINGS if name == encoding), "an unknown encoding")
        super().__init__(f"the byte-order mark names {name}, which Python cannot decode")
        self.encoding = encoding

    def __reduce__(self) -> tuple[type[UnsupportedBomError], tuple[str]]:
        return type(self), (self.encoding,)


def codec_for(info: BomInfo) -> str:
    codec = info.codec
    if codec is None:
        raise UnsupportedBomError(info.encoding)
    return codec


def strip(data: BytesLike, *, among: Iterable[str] | None = None) -> bytes:
    r"""Return ``data`` without its leading byte-order mark, unchanged if it has none.

    Only one mark is removed. ``among`` limits which marks count, as in `detect`.
    BOCU-1 is left unchanged because removing its mark would discard decoder state.
    Malformed UTF-7 runs are also left unchanged.

    >>> from sniffbom import strip
    >>> strip(b"\xef\xbb\xbfhello")
    b'hello'
    """
    data = byte_data(data)
    info = detect(data, among=among)
    if info is None or info.encoding == "bocu-1":
        return data
    if info.encoding == "utf-7":
        return strip_utf7(data)
    return data[info.length :]


def decode(
    data: BytesLike,
    default: str = "utf-8",
    *,
    errors: str = "strict",
    among: Iterable[str] | None = None,
) -> str:
    r"""Decode ``data`` with the encoding its byte-order mark implies, else ``default``.

    The mark is consumed, never left in the returned text; a second mark is kept as
    U+FEFF. ``errors`` is passed to the codec. Raises `UnsupportedBomError` when the mark
    names an encoding Python cannot decode.

    >>> from sniffbom import decode
    >>> decode(b"\xff\xfeh\x00i\x00")
    'hi'
    """
    data = byte_data(data)
    info = detect(data, among=among)
    if info is None:
        validate_codec(default, errors)
        return data.decode(default, errors)
    # Decoding the mark with the rest keeps UTF-7 exact, where it shares a byte.
    codec = codec_for(info)
    validate_codec(codec, errors)
    text = data.decode(codec, errors)
    return text[1:] if text.startswith("\ufeff") else text
