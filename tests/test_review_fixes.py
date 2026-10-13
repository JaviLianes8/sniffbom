"""Regression tests for the findings of the independent review."""

from __future__ import annotations

import codecs
import io
import json
import os
import stat
import sys
from pathlib import Path

import pytest

from sniffbom import (
    bom_sniff,
    decode,
    detect,
    needs_more,
    strip,
    text_stream,
    whatwg_decode,
    xml_autodetect,
)
from sniffbom._cli import main


class Stalling(io.RawIOBase):
    """A non-blocking reader: hands out its chunks in order, ``None`` meaning "no data yet"."""

    def __init__(self, *chunks: bytes | None) -> None:
        self._chunks = list(chunks)

    def readable(self) -> bool:
        return True

    def read(self, size: int = -1) -> bytes | None:
        return self._chunks.pop(0) if self._chunks else b""


def test_a_stalled_stream_does_not_decide_the_mark_early() -> None:
    with pytest.raises(BlockingIOError):
        text_stream(Stalling(b"\xff\xfe", None, b"\x00\x00", b"A\x00\x00\x00"))


def test_a_stall_after_the_mark_is_decided_is_fine() -> None:
    assert text_stream(Stalling(b"\xef\xbb\xbfh", b"i")).read() == "hi"


def test_a_utf7_run_with_six_spare_zero_bits_is_left_unchanged() -> None:
    assert strip(b"+/v8AA-") == b"+/v8AA-"
    assert strip(b"+/v8AAAAAA") == b"+/v8AAAAAA"


@pytest.mark.parametrize("kind", [bytearray, memoryview])
def test_bytes_like_input_is_accepted(kind: type) -> None:
    data = kind(codecs.BOM_UTF8 + b"hi")
    assert detect(data).encoding == "utf-8"  # type: ignore[union-attr]
    assert strip(data) == b"hi" and isinstance(strip(data), bytes)
    assert decode(data) == "hi"
    assert needs_more(kind(b"\xef\xbb")) is True
    assert bom_sniff(data) == "UTF-8"
    assert whatwg_decode(data) == "hi"
    assert xml_autodetect(kind(b"<?xml")).family == "ascii"
    assert strip(kind(b"plain")) == b"plain"


class Pipe:
    def __init__(self, data: bytes = b"") -> None:
        self.buffer = io.BytesIO(data)


def test_stripped_stdin_owns_stdout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    other = tmp_path / "a.txt"
    other.write_bytes(codecs.BOM_UTF8 + b"x")
    stdout = Pipe()
    monkeypatch.setattr(sys, "stdin", Pipe(codecs.BOM_UTF8 + b"hi"))
    monkeypatch.setattr(sys, "stdout", stdout)
    assert main(["--strip", "--json", str(other), "-"]) == 0
    assert stdout.buffer.getvalue() == b"hi"
    report = json.loads(capsys.readouterr().err)
    assert [(entry["path"], entry["stripped"]) for entry in report] == [
        (str(other), True),
        ("-", True),
    ]


def test_a_read_only_file_is_never_left_half_done(tmp_path: Path) -> None:
    target = tmp_path / "ro.txt"
    target.write_bytes(codecs.BOM_UTF8 + b"x")
    target.chmod(stat.S_IREAD)
    try:
        status = main(["--strip", str(target)])
        assert [p.name for p in tmp_path.iterdir()] == ["ro.txt"]
        # POSIX may replace the file in a writable folder; Windows refuses. Both are whole.
        assert (status, target.read_bytes()) in {(0, b"x"), (2, codecs.BOM_UTF8 + b"x")}
        assert not target.stat().st_mode & stat.S_IWRITE
    finally:
        target.chmod(stat.S_IREAD | stat.S_IWRITE)


def test_strip_follows_a_symlink(tmp_path: Path) -> None:
    target = tmp_path / "real.txt"
    target.write_bytes(codecs.BOM_UTF8 + b"x")
    link = tmp_path / "link.txt"
    try:
        os.symlink(target, link)
    except (OSError, NotImplementedError):
        pytest.skip("this system does not let us create a symlink")
    assert main(["--strip", str(link)]) == 0
    assert link.is_symlink()
    assert target.read_bytes() == b"x"


def test_malformed_utf7_is_not_reported_as_stripped(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = tmp_path / "bad.txt"
    target.write_bytes(b"+/v9x")
    assert main(["--strip", str(target)]) == 0
    assert target.read_bytes() == b"+/v9x"
    assert capsys.readouterr().out == f"{target}: utf-7 (4 bytes)\n"


def test_a_directory_is_named_as_such(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main([str(tmp_path)]) == 2
    assert "is a directory" in capsys.readouterr().err


def test_empty_among_items_are_ignored(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    target = tmp_path / "a.txt"
    target.write_bytes(codecs.BOM_UTF8)
    assert main(["--check", "--among", "utf-8,", str(target)]) == 1
    capsys.readouterr()
