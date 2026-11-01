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
@pytest.mark.parametrize("prefix", [b"", b"\xef\xbb\xbf"], ids=["unmarked", "marked"])
@pytest.mark.parametrize("payload", [b"", b"plain", b"\xff"], ids=["empty", "valid", "invalid"])
@pytest.mark.parametrize("surrogate", ["\ud800", "\udbff", "\udc00", "\udfff"])
@pytest.mark.parametrize("position", ["leading", "interior", "trailing"])
@pytest.mark.parametrize("kind", [str, PolicyName])
def test_surrogate_error_policies_raise_bounded_lookup_errors(
    entry: str, prefix: bytes, payload: bytes, surrogate: str, position: str, kind: type[str]
) -> None:
    padding = "PRIVATE" + "x" * 10000
    names = {
        "leading": surrogate + padding,
        "interior": padding + surrogate + "_handler",
        "trailing": padding + surrogate,
    }
    policy = kind(names[position])
    with pytest.raises(LookupError) as caught:
        _decode(entry, prefix + payload, policy)
    error = caught.value
    assert type(error) is LookupError
    assert error.args == ("unknown encoding or error handler",)
    assert str(error) == "unknown encoding or error handler"
    assert repr(error) == "LookupError('unknown encoding or error handler')"
    assert error.__cause__ is None and error.__context__ is None


@pytest.mark.parametrize("entry", ["bulk", "stream"])
@pytest.mark.parametrize("prefix", [b"", b"\xef\xbb\xbf"], ids=["unmarked", "marked"])
@pytest.mark.parametrize(
    "name",
    [
        "SniffbomMixedCaseHandler",
        " sniffbom_spaced_handler ",
        "sniffbom_\ud7ff_handler",
        "sniffbom_\ue000_handler",
    ],
)
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
    payload = b"a\xffb"
    expected = payload.decode("utf-8", name)
    assert expected == "a[handled]b"
    assert calls == [b"\xff"]
    calls.clear()
    assert _decode(entry, prefix + payload, kind(name)) == expected
    assert calls == [b"\xff"]


@pytest.mark.parametrize("entry", ["bulk", "stream"])
@pytest.mark.parametrize("prefix", [b"", b"\xef\xbb\xbf"], ids=["unmarked", "marked"])
def test_decoding_keeps_the_underlying_error_policy(entry: str, prefix: bytes) -> None:
    assert _decode(entry, prefix + b"a\xffb", PolicyName("ignore")) == "ab"
