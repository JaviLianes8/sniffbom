"""Redirected reports preserve CLI status and multi-file processing."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize("mode", [[], ["--check"], ["--strip"]])
@pytest.mark.parametrize("marked", [False, True])
def test_redirected_unicode_filenames(mode: list[str], marked: bool, tmp_path: Path) -> None:
    paths = [tmp_path / "\U0001f680.txt", tmp_path / "second.txt"]
    original = (b"\xef\xbb\xbf" if marked else b"") + b"hello"
    for path in paths:
        path.write_bytes(original)
    result = subprocess.run(
        [sys.executable, "-m", "sniffbom", *mode, *(str(path) for path in paths)],
        env={
            **os.environ,
            "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src"),
            "PYTHONIOENCODING": "cp1252:strict",
        },
        capture_output=True,
        timeout=300,
        check=False,
    )
    assert result.returncode == (1 if mode == ["--check"] and marked else 0), result.stderr
    assert result.stderr == b""
    assert len(result.stdout.splitlines()) == 2
    assert b"\\U0001f680.txt" in result.stdout
    assert all(
        path.read_bytes() == (b"hello" if mode == ["--strip"] else original) for path in paths
    )


def test_unicode_error_report_preserves_status_and_later_paths(tmp_path: Path) -> None:
    missing = tmp_path / "missing-\U0001f680.txt"
    later = tmp_path / "second.txt"
    later.write_bytes(b"\xef\xbb\xbfhello")
    program = (
        "import runpy, sys; "
        "sys.stderr.reconfigure(encoding='cp1252', errors='strict'); "
        "sys.argv = ['sniffbom', *sys.argv[1:]]; "
        "runpy.run_module('sniffbom', run_name='__main__')"
    )
    result = subprocess.run(
        [sys.executable, "-c", program, str(missing), str(later)],
        env={
            **os.environ,
            "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src"),
            "PYTHONIOENCODING": "cp1252:strict",
        },
        capture_output=True,
        timeout=300,
        check=False,
    )
    assert result.returncode == 2, result.stderr
    assert b"missing-\\U0001f680.txt" in result.stderr
    assert b"Traceback" not in result.stderr
    assert len(result.stderr.splitlines()) == 1
    assert b"second.txt: utf-8 (3 bytes)" in result.stdout
    assert len(result.stdout.splitlines()) == 1
    assert later.read_bytes() == b"\xef\xbb\xbfhello"
