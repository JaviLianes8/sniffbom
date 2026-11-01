"""Portable models supplement the real POSIX mode and symlink tests."""

from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

from sniffbom._cli import main


def test_replaceable_read_only_target_restores_mode(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "readonly"
    path.write_bytes(b"\xef\xbb\xbfhello")
    path.chmod(stat.S_IREAD)
    original_mode = path.stat().st_mode
    replace = os.replace

    def allow_replace(source: str, target: Path) -> None:
        # Model a writable POSIX directory allowing replacement of a read-only file.
        target.chmod(stat.S_IREAD | stat.S_IWRITE)
        replace(source, target)

    monkeypatch.setattr("sniffbom._cli.os.replace", allow_replace)
    try:
        assert main(["--strip", str(path)]) == 0
        assert path.read_bytes() == b"hello"
        assert path.stat().st_mode == original_mode
    finally:
        path.chmod(stat.S_IREAD | stat.S_IWRITE)


def test_resolved_alias_keeps_alias_and_updates_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target, alias = tmp_path / "target", tmp_path / "alias"
    target.write_bytes(b"\xef\xbb\xbfhello")
    alias.write_bytes(b"alias identity")
    read_bytes, resolve = Path.read_bytes, Path.resolve

    def read_alias(path: Path) -> bytes:
        return read_bytes(target if path == alias else path)

    def resolve_alias(path: Path, strict: bool = False) -> Path:
        return target if path == alias else resolve(path, strict=strict)

    monkeypatch.setattr(Path, "read_bytes", read_alias)
    monkeypatch.setattr(Path, "resolve", resolve_alias)
    assert main(["--strip", str(alias)]) == 0
    assert read_bytes(target) == b"hello"
    assert read_bytes(alias) == b"alias identity"
