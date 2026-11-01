"""Contracts for supported byte inputs, option errors and streaming setup."""

from __future__ import annotations

import io
from collections.abc import Callable
from typing import cast

import pytest

from sniffbom import (
    BomInfo,
    UnsupportedBomError,
    bom_sniff,
    decode,
    detect,
    needs_more,
    strip,
    text_stream,
    whatwg_decode,
    xml_autodetect,
)

BytesLike = bytes | bytearray | memoryview
READERS: tuple[Callable[[BytesLike], object], ...] = (
    detect,
    strip,
    decode,
    needs_more,
    bom_sniff,
    whatwg_decode,
    xml_autodetect,
)


@pytest.mark.parametrize("function", READERS)
@pytest.mark.parametrize("value", [0, 5, [], [239, 187, 191], "secret", None, object()])
def test_only_documented_byte_inputs_are_accepted(
    function: Callable[[BytesLike], object], value: object
) -> None:
    with pytest.raises(TypeError, match="data must be bytes, bytearray or memoryview"):
        function(cast(BytesLike, value))


@pytest.mark.parametrize("function", READERS)
def test_released_views_raise_value_error(function: Callable[[BytesLike], object]) -> None:
    view = memoryview(b"hello")
    view.release()
    with pytest.raises(ValueError):
        function(view)


@pytest.mark.parametrize("shape", ["wide", "matrix", "strided", "reversed", "scalar"])
def test_views_are_read_as_raw_bytes(shape: str) -> None:
    data = b"\xef\xbb\xbfhello"
    if shape == "wide":
        view = memoryview(data).cast("I")
    elif shape == "matrix":
        view = memoryview(data).cast("B", (2, 4))
    elif shape == "strided":
        view = memoryview(b"".join(bytes((byte, 0)) for byte in data))[::2]
    elif shape == "reversed":
        view = memoryview(data[::-1])[::-1]
    else:
        view = memoryview(data).cast("Q", ())
    assert detect(view) == BomInfo("utf-8", 3)
    assert strip(view) == b"hello"
    assert decode(view) == whatwg_decode(view) == "hello"
    assert bom_sniff(view) == "UTF-8"
    assert xml_autodetect(view).bom_length == 3
    assert not needs_more(view)


def test_byte_subclasses_cannot_override_the_buffer_contents() -> None:
    class Misleading(bytes):
        def __bytes__(self) -> bytes:
            return b"wrong"

    data = Misleading(b"\xef\xbb\xbfhello")
    assert decode(data) == "hello"
    assert strip(data) == b"hello"


@pytest.mark.parametrize("among", ["utf-8", b"utf-8", bytearray(), memoryview(b""), [1], [[]]])
def test_invalid_among_types_fail_consistently(among: object) -> None:
    for function in (detect, needs_more, strip, decode):
        with pytest.raises(TypeError):
            function(b"", among=cast(list[str], among))
    with pytest.raises(TypeError):
        text_stream(io.BytesIO(), among=cast(list[str], among))


def test_among_is_validated_without_echoing_unknown_values() -> None:
    secret = "SECRET" * 100000
    for function in (detect, needs_more, strip, decode):
        with pytest.raises(ValueError) as caught:
            function(b"", among=[secret])
        assert "SECRET" not in str(caught.value) and len(str(caught.value)) < 100
    with pytest.raises(ValueError):
        text_stream(io.BytesIO(), among=[secret])


def test_among_generators_duplicates_and_order_do_not_change_precedence() -> None:
    data = b"\xff\xfe\x00\x00"
    names = ["utf-16-le", "utf-32-le", "utf-16-le"]
    assert detect(data, among=iter(names)) == BomInfo("utf-32-le", 4)
    assert strip(data, among=iter(names)) == b""
    assert decode(data, among=iter(names)) == ""
    assert needs_more(b"\xff\xfe", among=iter(names))
    assert text_stream(io.BytesIO(data), among=iter(names)).read() == ""


@pytest.mark.parametrize("name", ["SECRET" * 10000, "missing-codec"])
def test_unknown_codec_and_handler_errors_are_bounded(name: str) -> None:
    operations: tuple[Callable[[], object], ...] = (
        lambda: decode(b"", name),
        lambda: decode(b"", errors=name),
        lambda: decode(b"\xef\xbb\xbfhi", errors=name),
        lambda: whatwg_decode(b"", name),
        lambda: text_stream(io.BytesIO(), name),
        lambda: text_stream(io.BytesIO(), errors=name),
    )
    for operation in operations:
        with pytest.raises(LookupError) as caught:
            operation()
        assert str(caught.value) == "unknown encoding or error handler"


def test_nul_options_and_wrong_types_have_safe_errors() -> None:
    for name in ("utf-8\0SECRET", "\0"):
        with pytest.raises(ValueError, match="must not contain NUL"):
            decode(b"", name)
        with pytest.raises(ValueError, match="must not contain NUL"):
            decode(b"", errors=name)
    with pytest.raises(TypeError):
        decode(b"", cast(str, 1))
    with pytest.raises(TypeError):
        decode(b"", errors=cast(str, None))
    with pytest.raises(LookupError):
        decode(b"", "base64_codec")


def test_unused_defaults_are_ignored_when_a_mark_selects_the_codec() -> None:
    data = b"\xef\xbb\xbfhello"
    assert decode(data, "nonexistent") == "hello"
    assert whatwg_decode(data, "nonexistent") == "hello"
    assert text_stream(io.BytesIO(data), "nonexistent").read() == "hello"


@pytest.mark.parametrize("newline", ["SECRET" * 10000, 1, b"\n"])
def test_invalid_newlines_fail_before_consuming_input(newline: object) -> None:
    raw = io.BytesIO(b"abc")
    with pytest.raises((TypeError, ValueError)) as caught:
        text_stream(raw, newline=cast(str, newline))
    assert raw.tell() == 0
    assert "SECRET" not in str(caught.value) and len(str(caught.value)) < 100


def test_unsupported_errors_do_not_echo_unknown_names() -> None:
    error = UnsupportedBomError("SECRET" * 100000)
    assert "SECRET" not in str(error) and len(str(error)) < 100
    with pytest.raises(TypeError):
        UnsupportedBomError(cast(str, 42))
