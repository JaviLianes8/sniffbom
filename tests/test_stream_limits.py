"""Bounded stream decoding and reader setup contracts."""

from __future__ import annotations

import io
from collections.abc import Iterable

import pytest

from sniffbom import decode, text_stream


class CountingReader(io.BytesIO):
    def __init__(self, raw: bytes, step: int = 8192) -> None:
        super().__init__(raw)
        self.consumed = 0
        self.step = step

    def read(self, size: int | None = -1) -> bytes:
        count = self.step if size is None or size < 0 else min(size, self.step)
        raw = super().read(count)
        self.consumed += len(raw)
        return raw


@pytest.mark.parametrize("count", [131072, 2097152])
@pytest.mark.parametrize("marked", [False, True])
def test_utf7_long_runs_fail_before_reading_unbounded_input(count: int, marked: bool) -> None:
    raw = (("\ufeff" if marked else "") + "\u1234" * count).encode("utf-7")
    reader = CountingReader(raw)
    with (
        pytest.raises(UnicodeError, match=r"^UTF-7 shifted run exceeds 65536 bytes$"),
        text_stream(reader, default="utf7") as stream,
    ):
        stream.read()
    assert reader.consumed <= 65536 + 8192


@pytest.mark.parametrize("prefix", [b"+", b"+/v8"])
@pytest.mark.parametrize("step", [97, 8192])
def test_utf7_run_limit_accepts_boundary_and_resets(prefix: bytes, step: int) -> None:
    run = prefix + b"A" * (65537 - len(prefix)) + b"-"
    raw = run + b"\n" + run + b"+-tail"
    with text_stream(CountingReader(raw, step), default="utf-7") as stream:
        assert stream.read() == decode(raw, default="utf-7")


@pytest.mark.parametrize("errors", ["strict", "replace", "ignore"])
@pytest.mark.parametrize("step", [97, 8192])
def test_first_byte_over_utf7_limit_is_rejected(errors: str, step: int) -> None:
    raw = b"+" + b"A" * 65537 + b"-"
    with (
        pytest.raises(UnicodeError, match=r"^UTF-7 shifted run exceeds 65536 bytes$"),
        text_stream(CountingReader(raw, step), default="utf-7", errors=errors) as stream,
    ):
        stream.read()


@pytest.mark.parametrize("step", [97, 8192])
def test_plus_counts_inside_utf7_shifted_run(step: int) -> None:
    raw = b"+" + b"+" * 65544 + b"-"
    assert len(raw.decode("utf-7")) == 24579
    with (
        pytest.raises(UnicodeError, match=r"^UTF-7 shifted run exceeds 65536 bytes$"),
        text_stream(CountingReader(raw, step), default="utf-7") as stream,
    ):
        stream.read()


@pytest.mark.parametrize("codec", ["utf-8", "latin-1"])
@pytest.mark.parametrize("step", [97, 8192])
def test_long_ascii_run_remains_valid_in_non_utf7_stream(codec: str, step: int) -> None:
    raw = b"+" + b"A" * 65537 + b"-"
    with text_stream(CountingReader(raw, step), default=codec) as stream:
        assert stream.read() == raw.decode(codec)
        assert stream.read() == ""


@pytest.mark.parametrize("marked", [False, True])
def test_utf7_limit_applies_to_runs_after_plain_text(marked: bool) -> None:
    raw = (b"+/v8-" if marked else b"") + b"plain" + b"+" + b"A" * 65539 + b"-"
    with (
        pytest.raises(UnicodeError, match=r"^UTF-7 shifted run exceeds 65536 bytes$"),
        text_stream(io.BytesIO(raw), default="utf-7") as stream,
    ):
        stream.read()


@pytest.mark.parametrize("raw", [bytes.fromhex("843195338130"), b"\x810", b""])
@pytest.mark.parametrize("codec", ["gb18030", "GB18030"])
def test_gb18030_surrogateescape_streams_are_rejected(raw: bytes, codec: str) -> None:
    with pytest.raises(LookupError, match=r"^GB18030 streams do not support surrogateescape$"):
        text_stream(io.BytesIO(raw), default=codec, errors="surrogateescape")
    with text_stream(
        io.BytesIO(b"\xef\xbb\xbf\x810"), default=codec, errors="surrogateescape"
    ) as stream:
        assert stream.read() == "\udc810"


@pytest.mark.parametrize("reader", [None, True, 1, b"", "", object()])
@pytest.mark.parametrize("among", [None, ()])
def test_invalid_readers_raise_bounded_type_errors(
    reader: object, among: Iterable[str] | None
) -> None:
    with pytest.raises(TypeError, match=r"^binary must provide callable read and close methods$"):
        text_stream(reader, among=among)  # type: ignore[arg-type]


def test_reader_capabilities_are_checked_before_consuming_input() -> None:
    class MissingClose:
        def read(self, size: int = -1) -> bytes:
            pytest.fail("invalid reader was consumed")

    with pytest.raises(TypeError):
        text_stream(MissingClose())  # type: ignore[arg-type]


@pytest.mark.parametrize("read", ["missing", None, False, 1, b""])
@pytest.mark.parametrize("among", [None, ()])
def test_closeable_reader_still_requires_callable_read(
    read: object, among: Iterable[str] | None
) -> None:
    class CloseOnly:
        read: object

        def close(self) -> None:
            pass

    reader = CloseOnly()
    if read != "missing":
        reader.read = read
    with pytest.raises(TypeError, match=r"^binary must provide callable read and close methods$"):
        text_stream(reader, among=among)  # type: ignore[arg-type]
