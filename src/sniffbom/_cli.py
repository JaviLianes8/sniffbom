"""Command line: name, check for or strip the byte-order mark of files."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path

from ._bom import strip
from ._table import ENCODINGS, BomInfo, detect


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sniffbom", description="Name, check for or strip the byte-order mark of files."
    )
    parser.add_argument("paths", nargs="+", metavar="PATH", help="files to read, - for stdin")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="exit 1 if any file has a mark")
    mode.add_argument(
        "--strip", action="store_true", help="remove the mark in place (stdin goes to stdout)"
    )
    parser.add_argument("--json", action="store_true", help="print one JSON array")
    parser.add_argument(
        "--among",
        metavar="NAMES",
        help=f"comma-separated encodings to look for, from: {', '.join(ENCODINGS)}",
    )
    return parser


def _rewrite(path: Path, data: bytes) -> None:
    # Write next to the real file (through any symlink) and swap it in, so a failure never
    # leaves half a file. The mode is copied after the swap: a read-only temporary file
    # could not be replaced or removed on Windows.
    target = path.resolve()
    handle, name = tempfile.mkstemp(dir=target.parent, prefix=f".{target.name}.")
    mode = target.stat().st_mode
    try:
        with os.fdopen(handle, "wb") as out:
            out.write(data)
        os.replace(name, target)
    except BaseException:
        Path(name).unlink(missing_ok=True)
        raise
    os.chmod(target, mode)


def _read(path: str) -> bytes:
    if path == "-":
        return sys.stdin.buffer.read()
    if Path(path).is_dir():
        raise IsADirectoryError(21, "is a directory")
    return Path(path).read_bytes()


def _line(path: str, info: BomInfo | None, stripped: bool) -> str:
    if info is None:
        return f"{path}: none"
    verb = "stripped " if stripped else ""
    return f"{path}: {verb}{info.encoding} ({info.length} bytes)"


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command line and return its exit status."""
    parser = _parser()
    args = parser.parse_args(argv)
    among = None
    if args.among is not None:
        among = [name.strip() for name in args.among.split(",") if name.strip()]
    try:
        detect(b"", among=among)
    except ValueError as error:
        parser.error(str(error))
    # Stripped stdin owns stdout, so the report goes to stderr instead.
    out = sys.stderr if args.strip and "-" in args.paths else sys.stdout
    report: list[dict[str, object]] = []
    found = failed = False
    for path in args.paths:
        try:
            data = _read(path)
            info = detect(data, among=among)
            stripped = False
            if args.strip:
                # A malformed UTF-7 run cannot be shortened exactly and stays as it is.
                new = strip(data, among=among)
                stripped = new != data
                if path == "-":
                    sys.stdout.buffer.write(new)
                    sys.stdout.buffer.flush()
                elif stripped:
                    _rewrite(Path(path), new)
        except OSError as error:
            print(f"sniffbom: {path}: {error.strerror or error}", file=sys.stderr)
            failed = True
            continue
        found = found or info is not None
        if args.json:
            encoding = None if info is None else info.encoding
            length = 0 if info is None else info.length
            report.append(
                {"path": path, "encoding": encoding, "length": length, "stripped": stripped}
            )
        else:
            print(_line(path, info, stripped), file=out)
    if args.json:
        print(json.dumps(report), file=out)
    if failed:
        return 2
    return 1 if args.check and found else 0
