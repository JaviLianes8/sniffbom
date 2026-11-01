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
