"""Codec validation and diagnostic boundaries, using handwritten inputs."""

from __future__ import annotations

import io

import pytest

from sniffbom import UnsupportedBomError, decode, text_stream, whatwg_decode


def _decode(entry: str, raw: bytes, codec: str, errors: str = "replace") -> str:
    if entry == "bulk":
        return decode(raw, default=codec, errors=errors)
    if entry == "whatwg":
        return whatwg_decode(raw, fallback=codec)
    with text_stream(io.BytesIO(raw), default=codec, errors=errors) as stream:
        return stream.read()


@pytest.mark.parametrize("entry", ["bulk", "whatwg", "stream"])
@pytest.mark.parametrize("codec", ["\ud800", "\udfff", "PRIVATE" * 10000 + "\ud800"])
def test_surrogate_codec_names_raise_bounded_lookup_errors(entry: str, codec: str) -> None:
    with pytest.raises(LookupError) as caught:
        _decode(entry, b"", codec)
    assert len(str(caught.value)) < 100
    assert "PRIVATE" not in str(caught.value)
    assert _decode(entry, b"\xef\xbb\xbfok", codec) == "ok"


@pytest.mark.parametrize("entry", ["bulk", "whatwg", "stream"])
@pytest.mark.parametrize("codec", ["idna", "IDNA", "undefined"])
@pytest.mark.parametrize("raw", [b"", b"example.com"])
def test_incompatible_text_codecs_raise_bounded_lookup_errors(
    entry: str, codec: str, raw: bytes
) -> None:
    with pytest.raises(LookupError) as caught:
        _decode(entry, raw, codec)
    assert len(str(caught.value)) < 100
    assert _decode(entry, b"\xef\xbb\xbfok", codec) == "ok"


@pytest.mark.parametrize("entry", ["bulk", "stream"])
def test_idna_strict_remains_supported(entry: str) -> None:
    assert _decode(entry, b"example.com", "idna", "strict") == "example.com"
    with pytest.raises(LookupError):
        _decode(entry, b"example.com", "undefined", "strict")


@pytest.mark.parametrize("entry", ["bulk", "stream"])
@pytest.mark.parametrize("errors", ["surrogateescape", "backslashreplace", "surrogatepass"])
def test_punycode_rejects_unsupported_error_policies(entry: str, errors: str) -> None:
    with pytest.raises(LookupError, match="encoding does not support the requested error policy"):
        _decode(entry, b"example-", "punycode", errors)


@pytest.mark.parametrize("entry", ["bulk", "stream"])
@pytest.mark.parametrize("errors", ["strict", "replace", "ignore"])
def test_punycode_supported_error_policies(entry: str, errors: str) -> None:
    assert _decode(entry, b"example-", "punycode", errors) == "example"


class UntrustedName(str):
    def __eq__(self, other: object) -> bool:
        return True

    def __str__(self) -> str:
        return "PRIVATE" * 10000

    def __format__(self, spec: str) -> str:
        return str(self)


@pytest.mark.parametrize("value", ["PRIVATE" * 10000, "scsu"])
def test_unsupported_diagnostics_use_only_canonical_names(value: str) -> None:
    error = UnsupportedBomError(UntrustedName(value))
    assert len(str(error)) < 100
    assert "PRIVATE" not in str(error)
    assert type(error.encoding) is str
    assert error.encoding == value
    assert ("scsu" in str(error)) is (value == "scsu")
