"""Exact error-policy names and safe validation, using handwritten inputs."""

from __future__ import annotations

import codecs
import io
from collections.abc import Iterator

import pytest

from sniffbom import decode, text_stream


class PolicyName(str):
    def __str__(self) -> str:
        return "strict"

    def __iter__(self) -> Iterator[str]:
        raise AssertionError("policy iteration override was called")

    def __contains__(self, value: object) -> bool:
        raise AssertionError("policy containment override was called")


def _decode(entry: str, raw: bytes, errors: str) -> str:
    if entry == "bulk":
        return decode(raw, errors=errors)
    with text_stream(io.BytesIO(raw), errors=errors) as stream:
        text = stream.read()
        assert stream.read() == ""
        return text


@pytest.mark.parametrize("entry", ["bulk", "stream"])
@pytest.mark.parametrize("raw", [b"", b"plain", b"\xef\xbb\xbf", b"\xef\xbb\xbfplain"])
@pytest.mark.parametrize("surrogate", ["\ud800", "\udbff", "\udc00", "\udfff"])
@pytest.mark.parametrize("kind", [str, PolicyName])
def test_surrogate_error_policies_raise_bounded_lookup_errors(
    entry: str, raw: bytes, surrogate: str, kind: type[str]
) -> None:
    policy = kind("PRIVATE" + "x" * 10000 + surrogate)
    with pytest.raises(LookupError) as caught:
        _decode(entry, raw, policy)
    error = caught.value
    assert type(error) is LookupError
    assert error.args == ("unknown encoding or error handler",)
    assert str(error) == "unknown encoding or error handler"
    assert repr(error) == "LookupError('unknown encoding or error handler')"
    assert error.__cause__ is None and error.__context__ is None


@pytest.mark.parametrize("entry", ["bulk", "stream"])
@pytest.mark.parametrize("prefix", [b"", b"\xef\xbb\xbf"], ids=["unmarked", "marked"])
@pytest.mark.parametrize("name", ["SniffbomMixedCaseHandler", " sniffbom_spaced_handler "])
@pytest.mark.parametrize("kind", [str, PolicyName])
def test_registered_error_handler_names_are_exact(
    entry: str, prefix: bytes, name: str, kind: type[str]
) -> None:
    calls: list[bytes] = []

    def handler(error: UnicodeError) -> tuple[str, int]:
        assert isinstance(error, UnicodeDecodeError)
        calls.append(error.object[error.start : error.end])
        return "[handled]", error.end

    codecs.register_error(name, handler)
    assert _decode(entry, prefix + b"a\xffb", kind(name)) == "a[handled]b"
    assert calls == [b"\xff"]


@pytest.mark.parametrize("entry", ["bulk", "stream"])
@pytest.mark.parametrize("prefix", [b"", b"\xef\xbb\xbf"], ids=["unmarked", "marked"])
def test_decoding_keeps_the_underlying_error_policy(entry: str, prefix: bytes) -> None:
    assert _decode(entry, prefix + b"a\xffb", PolicyName("ignore")) == "ab"
