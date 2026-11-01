"""Exact return, record, setup and diagnostic boundaries."""

from __future__ import annotations

import io
from pathlib import Path
from typing import cast

import pytest

from sniffbom import XmlFamily, XmlGuess, strip, text_stream
from sniffbom._cli import main


@pytest.mark.parametrize("kind", [bytes, bytearray, memoryview])
@pytest.mark.parametrize("raw", [b"", b"plain", b"\xef\xbb\xbfplain"])
def test_strip_always_returns_bytes_when_matching_is_disabled(kind: type, raw: bytes) -> None:
    result = strip(kind(raw), among=())
    assert type(result) is bytes
    assert result == raw


@pytest.mark.parametrize("kind", [bytes, bytearray, memoryview])
@pytest.mark.parametrize("raw", [b"", b"plain"])
def test_unmarked_strip_always_returns_bytes(kind: type, raw: bytes) -> None:
    assert type(strip(kind(raw))) is bytes


@pytest.mark.parametrize("length", [-123, -1, 0, 123])
def test_xmlguess_preserves_supplied_fields(length: int) -> None:
    family = cast(XmlFamily, "caller family")
    codec = "caller codec"
    record = XmlGuess(family, length, codec)
    assert (record.family, record.bom_length, record.codec) == (family, length, codec)


def test_empty_among_never_reads_during_setup() -> None:
    class Unreadable(io.BytesIO):
        def read(self, size: int | None = -1) -> bytes:
            pytest.fail("setup read despite empty among")

    raw = Unreadable()
    with text_stream(raw, among=()):
        assert raw.tell() == 0
    assert raw.closed


@pytest.mark.parametrize("reverse", [False, True])
def test_check_remembers_any_marked_file(reverse: bool, tmp_path: Path) -> None:
    marked, plain = tmp_path / "marked", tmp_path / "plain"
    marked.write_bytes(b"\xef\xbb\xbfhello")
    plain.write_bytes(b"hello")
    paths = [str(marked), str(plain)]
    assert main(["--check", *(reversed(paths) if reverse else paths)]) == 1


@pytest.mark.parametrize("length", [240, 241])
def test_diagnostic_path_limit_is_exact(
    length: int, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def fail(path: Path) -> bytes:
        raise OSError(5, "read failed")

    monkeypatch.setattr(Path, "read_bytes", fail)
    path = "x" * length
    assert main([path]) == 2
    label = path if length == 240 else "<invalid or oversized path>"
    assert capsys.readouterr().err == f"sniffbom: {label}: read failed\n"


@pytest.mark.parametrize("length", [160, 161, 10000])
def test_os_diagnostic_limit_is_exact(
    length: int, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def fail(path: Path) -> bytes:
        raise OSError(5, "x" * length)

    monkeypatch.setattr(Path, "read_bytes", fail)
    assert main(["missing"]) == 2
    assert capsys.readouterr().err == f"sniffbom: missing: {'x' * 160}\n"
