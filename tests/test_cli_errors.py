"""Bounded CLI diagnostics and safe replacement failures."""

from __future__ import annotations

import codecs
from pathlib import Path

import pytest

from sniffbom._cli import main


@pytest.mark.parametrize(
    "argument", ["--SECRET" * 10000, "--among=SECRET" * 10000], ids=["unknown", "among"]
)
def test_usage_errors_do_not_echo_arguments(
    argument: str, capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit) as caught:
        main([argument, "file"])
    assert caught.value.code == 2
    error = capsys.readouterr().err
    assert len(error) < 500 and "SECRET" not in error


@pytest.mark.parametrize(
    "path", ["SECRET" * 10000, "bad\0SECRET", "bad\nSECRET"], ids=["long", "nul", "newline"]
)
def test_bad_paths_return_two_with_bounded_messages(
    path: str, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main([path]) == 2
    error = capsys.readouterr().err
    assert len(error) < 500 and "SECRET" not in error


def test_failed_replace_keeps_original_and_removes_temporary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "input"
    path.write_bytes(codecs.BOM_UTF8 + b"content")

    def refuse(source: str, target: Path) -> None:
        raise PermissionError(13, "permission denied")

    monkeypatch.setattr("sniffbom._cli.os.replace", refuse)
    assert main(["--strip", str(path)]) == 2
    assert path.read_bytes() == codecs.BOM_UTF8 + b"content"
    assert list(tmp_path.iterdir()) == [path]
    assert "permission denied" in capsys.readouterr().err
