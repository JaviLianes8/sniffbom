"""Partial reads and streams: `needs_more` and `text_stream`."""

from __future__ import annotations

import codecs
import io

import pytest

from sniffbom import UnsupportedBomError, needs_more, text_stream


class Trickle(io.RawIOBase):
    """A non-seekable reader that hands out at most ``step`` bytes per call."""

    def __init__(self, data: bytes, step: int = 1) -> None:
        self._data = data
        self._step = step
        self.requested: list[int] = []

    def readable(self) -> bool:
        return True

    def read(self, size: int = -1) -> bytes:
        self.requested.append(size)
        count = self._step if size < 0 else min(size, self._step)
        chunk, self._data = self._data[:count], self._data[count:]
        return chunk

    def seekable(self) -> bool:
        return False

    def seek(self, offset: int, whence: int = 0) -> int:
        raise AssertionError("text_stream must not seek")


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (b"", True),
        (b"\xff", True),
        (b"\xff\xfe", True),
        (b"\xff\xfe\x00", True),
        (b"\xff\xfe\x00\x00", False),
        (b"\xff\xfeA", False),
        (b"\xef\xbb", True),
        (b"\xef\xbb\xbf", False),
        (b"+/v8", True),
        (b"+/v8-", False),
        (b"+/v9", False),
        (b"A", False),
    ],
)
def test_needs_more_says_whether_the_answer_can_still_change(data: bytes, expected: bool) -> None:
    assert needs_more(data) is expected


def test_needs_more_honours_among() -> None:
    assert needs_more(b"\xff\xfe") is True
    assert needs_more(b"\xff\xfe", among=["utf-16-le"]) is False
    assert needs_more(b"", among=()) is False


@pytest.mark.parametrize("encoding", ["utf-8", "utf-16-le", "utf-16-be", "utf-32-le", "utf-7"])
@pytest.mark.parametrize("step", [1, 2, 3, 64])
def test_text_stream_consumes_the_mark(encoding: str, step: int) -> None:
    text = "caf\xe9\nline \U0001f600\n"
    with text_stream(Trickle(("﻿" + text).encode(encoding), step)) as stream:
        assert stream.read() == text


def test_text_stream_uses_the_default_without_a_mark() -> None:
    assert text_stream(io.BytesIO(b"caf\xe9"), "latin-1").read() == "caf\xe9"


def test_text_stream_reads_only_what_it_needs_before_decoding() -> None:
    raw = Trickle(codecs.BOM_UTF16_LE + "hi".encode("utf-16-le"), step=1)
    stream = text_stream(raw)
    assert raw.requested == [5, 4, 3]
    assert stream.read() == "hi"


def test_text_stream_short_stream_is_fine() -> None:
    assert text_stream(io.BytesIO(b"\xff\xfe")).read() == ""
    assert text_stream(io.BytesIO(b"")).read() == ""


def test_text_stream_keeps_a_second_mark() -> None:
    assert text_stream(io.BytesIO(codecs.BOM_UTF8 * 2)).read() == "﻿"


def test_text_stream_passes_errors_and_newline() -> None:
    data = codecs.BOM_UTF8 + b"a\xff\r\nb"
    stream = text_stream(io.BytesIO(data), errors="replace", newline="")
    assert stream.read() == "a�\r\nb"


def test_text_stream_honours_among() -> None:
    data = b"\xff\xfe\x00\x00A\x00"
    assert text_stream(io.BytesIO(data), among=["utf-16-le", "utf-8"]).read() == "\x00A"


def test_text_stream_refuses_schemes_python_cannot_read() -> None:
    with pytest.raises(UnsupportedBomError):
        text_stream(io.BytesIO(b"\xfb\xee\x28x"))


def test_closing_the_text_stream_closes_the_binary() -> None:
    raw = io.BytesIO(codecs.BOM_UTF8 + b"x")
    text_stream(raw).close()
    assert raw.closed
