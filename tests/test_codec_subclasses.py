"""Codec options use underlying string values, with handwritten adversarial subclasses."""

from __future__ import annotations

import io
from collections.abc import Iterator

import pytest

from sniffbom import decode, text_stream, whatwg_decode


class NeverEqual(str):
    def __eq__(self, other: object) -> bool:
        return False


class AlwaysEqual(str):
    def __eq__(self, other: object) -> bool:
        return True


class HiddenName(str):
    def __iter__(self) -> Iterator[str]:
        return iter(())

    def __contains__(self, value: object) -> bool:
        return False

    def __str__(self) -> str:
        return "utf-8"


def _decode(entry: str, raw: bytes, codec: str, errors: str = "replace") -> str:
    if entry == "bulk":
        return decode(raw, default=codec, errors=errors)
    if entry == "whatwg":
        return whatwg_decode(raw, fallback=codec)
    with text_stream(io.BytesIO(raw), default=codec, errors=errors) as stream:
        return stream.read()


@pytest.mark.parametrize("entry", ["bulk", "whatwg", "stream"])
@pytest.mark.parametrize("name", ["\ud800", "PRIVATE" * 10000 + "\udfff"])
def test_subclass_surrogate_names_raise_bounded_lookup_errors(entry: str, name: str) -> None:
    with pytest.raises(LookupError, match=r"^unknown encoding or error handler$"):
        _decode(entry, b"", HiddenName(name))
    assert _decode(entry, b"\xef\xbb\xbfok", HiddenName(name)) == "ok"


@pytest.mark.parametrize("entry", ["bulk", "whatwg", "stream"])
def test_subclass_nul_names_raise_bounded_value_errors(entry: str) -> None:
    with pytest.raises(ValueError, match=r"^encoding and errors must not contain NUL$"):
        _decode(entry, b"", HiddenName("PRIVATE\x00"))


@pytest.mark.parametrize("entry", ["bulk", "stream"])
@pytest.mark.parametrize("codec,errors", [("idna", "replace"), ("punycode", "surrogateescape")])
def test_subclass_policies_cannot_bypass_codec_restrictions(
    entry: str, codec: str, errors: str
) -> None:
    with pytest.raises(
        LookupError, match=r"^encoding does not support the requested error policy$"
    ):
        _decode(entry, b"a", HiddenName(codec), AlwaysEqual(errors))


@pytest.mark.parametrize("entry", ["bulk", "stream"])
@pytest.mark.parametrize(
    "codec,raw,text", [("idna", b"example.com", "example.com"), ("utf8", b"ok", "ok")]
)
def test_subclass_options_preserve_supported_decoding(
    entry: str, codec: str, raw: bytes, text: str
) -> None:
    assert _decode(entry, raw, HiddenName(codec), NeverEqual("strict")) == text


@pytest.mark.parametrize("entry", ["bulk", "stream"])
def test_subclass_nul_policies_raise_bounded_value_errors(entry: str) -> None:
    with pytest.raises(ValueError, match=r"^encoding and errors must not contain NUL$"):
        _decode(entry, b"", "utf-8", HiddenName("PRIVATE\x00"))


@pytest.mark.parametrize("raw", [bytes.fromhex("843195338130"), b"\x810", b""])
def test_subclass_policy_cannot_bypass_gb18030_stream_restriction(raw: bytes) -> None:
    with pytest.raises(LookupError, match=r"^GB18030 streams do not support surrogateescape$"):
        text_stream(
            io.BytesIO(raw), default=HiddenName("GB18030"), errors=NeverEqual("surrogateescape")
        )
    with text_stream(
        io.BytesIO(b"\xef\xbb\xbf\x810"),
        default=HiddenName("GB18030"),
        errors=NeverEqual("surrogateescape"),
    ) as stream:
        assert stream.read() == "\udc810"
        assert stream.read() == ""


def test_whatwg_uses_underlying_subclass_fallback() -> None:
    assert whatwg_decode(b"\xe9", fallback=HiddenName("latin-1")) == "\xe9"
