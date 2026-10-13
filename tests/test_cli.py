"""The command line, driven in process through `main`."""

from __future__ import annotations

import codecs
import io
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from sniffbom._cli import main


@pytest.fixture
def files(tmp_path: Path) -> dict[str, Path]:
    paths = {
        "marked": tmp_path / "marked.txt",
        "plain": tmp_path / "plain.txt",
        "wide": tmp_path / "wide.txt",
    }
    paths["marked"].write_bytes(codecs.BOM_UTF8 + b"hi")
    paths["plain"].write_bytes(b"hi")
    paths["wide"].write_bytes(codecs.BOM_UTF16_LE + "hi".encode("utf-16-le"))
    return paths


class FakeStdin:
    def __init__(self, data: bytes) -> None:
        self.buffer = io.BytesIO(data)


class FakeStdout:
    def __init__(self) -> None:
        self.buffer = io.BytesIO()


def test_names_the_mark_of_each_file(
    files: dict[str, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    assert main([str(files["marked"]), str(files["plain"])]) == 0
    assert capsys.readouterr().out.splitlines() == [
        f"{files['marked']}: utf-8 (3 bytes)",
        f"{files['plain']}: none",
    ]


def test_check_exits_one_when_a_mark_is_found(
    files: dict[str, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["--check", str(files["plain"])]) == 0
    assert main(["--check", str(files["plain"]), str(files["marked"])]) == 1
    capsys.readouterr()


def test_strip_rewrites_in_place_and_keeps_the_rest(
    files: dict[str, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["--strip", str(files["marked"]), str(files["plain"]), str(files["wide"])]) == 0
    assert files["marked"].read_bytes() == b"hi"
    assert files["plain"].read_bytes() == b"hi"
    assert files["wide"].read_bytes() == "hi".encode("utf-16-le")
    out = capsys.readouterr().out
    assert "stripped utf-8 (3 bytes)" in out and "stripped utf-16-le (2 bytes)" in out
    assert sorted(p.name for p in files["marked"].parent.iterdir()) == [
        "marked.txt",
        "plain.txt",
        "wide.txt",
    ]


@pytest.mark.skipif(os.name == "nt", reason="file modes are POSIX")
def test_strip_keeps_the_file_mode(files: dict[str, Path]) -> None:
    files["marked"].chmod(0o751)
    main(["--strip", str(files["marked"])])
    assert files["marked"].stat().st_mode & 0o777 == 0o751


def test_json_report(files: dict[str, Path], capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--json", str(files["wide"]), str(files["plain"])]) == 0
    assert json.loads(capsys.readouterr().out) == [
        {"path": str(files["wide"]), "encoding": "utf-16-le", "length": 2, "stripped": False},
        {"path": str(files["plain"]), "encoding": None, "length": 0, "stripped": False},
    ]


def test_among_narrows_the_search(
    files: dict[str, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["--check", "--among", "utf-16-le, utf-16-be", str(files["marked"])]) == 0
    assert capsys.readouterr().out.strip().endswith(": none")


def test_unknown_among_name_is_a_usage_error(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as caught:
        main(["--among", "utf16", "x"])
    assert caught.value.code == 2
    assert "utf16" in capsys.readouterr().err


def test_missing_file_exits_two_and_goes_on(
    files: dict[str, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    missing = files["plain"].parent / "missing.txt"
    assert main([str(missing), str(files["marked"])]) == 2
    captured = capsys.readouterr()
    assert "missing.txt" in captured.err
    assert "utf-8 (3 bytes)" in captured.out


def test_stdin_is_read_and_stripped_to_stdout(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "stdin", FakeStdin(codecs.BOM_UTF8 + b"hi"))
    out = FakeStdout()
    monkeypatch.setattr(sys, "stdout", out)
    assert main(["--strip", "-"]) == 0
    assert out.buffer.getvalue() == b"hi"


def test_stdin_is_named(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", FakeStdin(b"\x84\x31\x95\x33"))
    assert main(["-"]) == 0
    assert capsys.readouterr().out == "-: gb18030 (4 bytes)\n"


def test_check_and_strip_are_exclusive(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as caught:
        main(["--check", "--strip", "x"])
    assert caught.value.code == 2
    capsys.readouterr()


def test_runs_as_a_module(files: dict[str, Path]) -> None:
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")}
    result = subprocess.run(
        [sys.executable, "-m", "sniffbom", "--check", str(files["wide"])],
        capture_output=True,
        env=env,
        check=False,
    )
    assert result.returncode == 1
    assert result.stdout.decode().strip().endswith("utf-16-le (2 bytes)")
