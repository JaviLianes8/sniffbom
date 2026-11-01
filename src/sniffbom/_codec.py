"""Validate codec options without including caller input in lookup errors."""

from __future__ import annotations

import codecs


def validate_codec(codec: str, errors: str) -> None:
    if not isinstance(codec, str) or not isinstance(errors, str):
        raise TypeError("encoding and errors must be strings")
    if "\x00" in codec or "\x00" in errors:
        raise ValueError("encoding and errors must not contain NUL")
    try:
        info = codecs.lookup(codec)
        codecs.lookup_error(errors)
    except LookupError:
        raise LookupError("unknown encoding or error handler") from None
    if not getattr(info, "_is_text_encoding", True):
        raise LookupError("encoding must be a text codec")
