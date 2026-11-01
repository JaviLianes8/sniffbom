"""Validate codec options without including caller input in lookup errors."""

from __future__ import annotations

import codecs


def validate_codec(codec: str, errors: str) -> tuple[str, str, str]:
    """Return plain codec and policy strings plus the codec's canonical name."""
    if not isinstance(codec, str) or not isinstance(errors, str):
        raise TypeError("encoding and errors must be strings")
    codec = str.__str__(codec)
    errors = str.__str__(errors)
    if "\x00" in codec or "\x00" in errors:
        raise ValueError("encoding and errors must not contain NUL")
    if any("\ud800" <= char <= "\udfff" for name in (codec, errors) for char in name):
        raise LookupError("unknown encoding or error handler")
    try:
        info = codecs.lookup(codec)
        codecs.lookup_error(errors)
    except LookupError:
        raise LookupError("unknown encoding or error handler") from None
    if not getattr(info, "_is_text_encoding", True):
        raise LookupError("encoding must be a text codec")
    policies = {"undefined": (), "idna": ("strict",), "punycode": ("strict", "replace", "ignore")}
    if info.name in policies and errors not in policies[info.name]:
        raise LookupError("encoding does not support the requested error policy")
    return codec, errors, info.name
