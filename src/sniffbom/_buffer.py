"""Read bytes-like inputs independently of their element format or shape."""

from __future__ import annotations

from typing import TypeAlias

BytesLike: TypeAlias = bytes | bytearray | memoryview


def _view(data: BytesLike) -> memoryview:
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise TypeError("data must be bytes, bytearray or memoryview")
    return memoryview(data)


def byte_data(data: BytesLike) -> bytes:
    return _view(data).tobytes()


def byte_head(data: BytesLike, size: int) -> bytes:
    view = _view(data)
    if view.c_contiguous:
        return view.cast("B")[:size].tobytes()
    return view.tobytes()[:size]
