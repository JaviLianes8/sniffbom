"""Open a binary stream as text with its byte-order mark consumed."""

from __future__ import annotations

import io
from collections.abc import Iterable
from typing import Protocol

from ._bom import codec_for
from ._table import detect, needs_more


class _Reader(Protocol):
    """Anything with a blocking ``read(size)`` and ``close()``: files, pipes, sockets."""

    def read(self, size: int = ..., /) -> bytes | None: ...

    def close(self) -> None: ...


class _Prefixed(io.RawIOBase):
    """A raw reader that serves the already read ``head`` and then the inner stream."""

    def __init__(self, head: bytes, inner: _Reader) -> None:
        self._head = head
        self._inner = inner

    def readable(self) -> bool:
        return True

    def readinto(self, buffer: memoryview) -> int | None:  # type: ignore[override]
        if self._head:
            count = min(len(buffer), len(self._head))
            buffer[:count] = self._head[:count]
            self._head = self._head[count:]
            return count
        chunk = self._inner.read(len(buffer))
        if chunk is None:
            return None
        buffer[: len(chunk)] = chunk
        return len(chunk)

    def close(self) -> None:
        if not self.closed:
            self._inner.close()
        super().close()


def text_stream(
    binary: _Reader,
    default: str = "utf-8",
    *,
    errors: str = "strict",
    among: Iterable[str] | None = None,
    newline: str | None = None,
) -> io.TextIOWrapper:
    """Wrap a binary stream as text, decoded as its byte-order mark says, else ``default``.

    Only the few bytes needed to decide are read up front and the stream is never
    seeked, so pipes and sockets work. The mark is consumed. Closing the result closes
    ``binary``. Raises `UnsupportedBomError` when the mark names an encoding Python
    cannot decode.
    """
    marks = None if among is None else tuple(among)
    head = b""
    while needs_more(head, among=marks):
        chunk = binary.read(5 - len(head))
        if not chunk:
            break
        head += chunk
    info = detect(head, among=marks)
    codec = default if info is None else codec_for(info)
    if info is not None and info.encoding != "utf-7":
        head = head[info.length :]
    reader = io.BufferedReader(_Prefixed(head, binary))
    text = io.TextIOWrapper(reader, encoding=codec, errors=errors, newline=newline)
    if info is not None and info.encoding == "utf-7":
        # A UTF-7 mark may share its last byte with the next character, so it cannot be
        # cut as bytes: the codec decodes it as U+FEFF and one character is read past it.
        text.read(1)
    return text
