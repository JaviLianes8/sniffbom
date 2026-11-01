"""Build the wheel, install it in a throwaway venv and drive the installed package.

Slow and needs the build backend, so it runs only with SNIFFBOM_E2E=1. Set
SNIFFBOM_E2E_NO_SCRIPT=1 where policy blocks running the generated console script.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import venv
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

pytestmark = pytest.mark.skipif(
    os.environ.get("SNIFFBOM_E2E") != "1", reason="set SNIFFBOM_E2E=1 to build and install"
)

PROGRAM = r"""
import importlib.metadata, importlib.resources, io
import sniffbom
from sniffbom import (
    ENCODINGS, BomInfo, UnsupportedBomError, XmlGuess, bom_sniff, decode, detect,
    needs_more, strip, text_stream, whatwg_decode, xml_autodetect,
)

assert "site-packages" in sniffbom.__file__, sniffbom.__file__
assert importlib.metadata.version("sniffbom") == sniffbom.__version__
assert importlib.resources.files("sniffbom").joinpath("py.typed").is_file()
assert len(ENCODINGS) == 11
assert detect(b"\xff\xfe\x00\x00") == BomInfo("utf-32-le", 4)
assert detect(b"\xff\xfe\x00\x00", among=("utf-16-le",)) == BomInfo("utf-16-le", 2)
assert decode(b"\x84\x31\x95\x33caf\xa8\xa6") == "caf\xe9"
assert strip(b"+/v8A6Q-") == b"+AOk-" and decode(b"+/v8A6Q-") == "\xe9"
assert needs_more(b"\xef\xbb") and not needs_more(b"\xef\xbb\xbf")
assert text_stream(io.BytesIO(b"\xfe\xff\x00h\x00i")).read() == "hi"
assert bom_sniff(b"\xff\xfe\x00\x00") == "UTF-16LE"
assert whatwg_decode(b"\xef\xbb\xbfa\xff", "latin-1") == "a\ufffd"
assert xml_autodetect(b"<?xml") == XmlGuess("ascii", 0, None)
try:
    decode(b"\xfb\xee\x28x")
except UnsupportedBomError as error:
    assert isinstance(error, LookupError) and error.encoding == "bocu-1"
else:
    raise AssertionError("expected UnsupportedBomError")
print("e2e ok")
"""


def _run(
    *cmd: str | Path,
    cwd: Path | None = None,
    stdin: bytes = b"",
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [str(c) for c in cmd],
        cwd=cwd,
        input=stdin,
        env=env,
        capture_output=True,
        check=False,
        timeout=240,
    )


def test_installed_wheel_end_to_end(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    built = _run(sys.executable, "-m", "build", "--outdir", dist, ROOT)
    assert built.returncode == 0, built.stderr
    (wheel,) = dist.glob("sniffbom-*.whl")
    (sdist,) = dist.glob("sniffbom-*.tar.gz")
    names = zipfile.ZipFile(wheel).namelist()
    assert "sniffbom/py.typed" in names and "sniffbom/__main__.py" in names
    assert not any(name.startswith(("tests/", "scripts/")) for name in names)
    entry_points = next(name for name in names if name.endswith("entry_points.txt"))
    assert "sniffbom = sniffbom._cli:main" in zipfile.ZipFile(wheel).read(entry_points).decode()
    listing = _run(sys.executable, "-m", "tarfile", "-l", sdist).stdout.decode()
    assert "IMPROVEMENTS-round" not in listing and "upstream/wpt" not in listing
    assert ".html" not in listing and "rfc2152" not in listing
    assert "tests/upstream/MANIFEST.json" in listing
    assert "tests/test_sources.py" in listing and "scripts/fetch_upstream.py" in listing
    assert "GUIDE.md" in listing and "LICENSE" in listing
    assert "CERT-1.0-REPORT" not in listing
    assert "__pycache__" not in listing and ".pyc" not in listing
    assert any(name.endswith("/LICENSE") for name in names)

    env_dir = tmp_path / "venv"
    venv.create(env_dir, with_pip=True)
    bindir = env_dir / ("Scripts" if sys.platform == "win32" else "bin")
    python = bindir / "python"
    work = tmp_path / "work"
    work.mkdir()
    if os.environ.get("SNIFFBOM_E2E_PYPI") == "1":
        previous = _run(python, "-m", "pip", "install", "-q", "sniffbom==0.2.0")
        assert previous.returncode == 0, previous.stderr
        baseline = _run(python, "-I", "-c", PROGRAM, cwd=work)
        assert baseline.returncode == 0, baseline.stderr
        snapshot = _run(
            python,
            "-I",
            "-c",
            "import pickle, pathlib, sniffbom; "
            "assert sniffbom.__version__ == '0.2.0'; "
            "pathlib.Path('old.pkl').write_bytes(pickle.dumps("
            "(sniffbom.BomInfo('utf-8', 3), sniffbom.XmlGuess('utf-8', 3, 'utf-8'))))",
            cwd=work,
        )
        assert snapshot.returncode == 0, snapshot.stderr
    installed = _run(python, "-m", "pip", "install", "-q", wheel)
    assert installed.returncode == 0, installed.stderr
    if os.environ.get("SNIFFBOM_E2E_PYPI") == "1":
        upgraded = _run(
            python,
            "-I",
            "-c",
            "import pickle, pathlib, sniffbom; "
            "assert sniffbom.__version__ == '1.0.0'; "
            "assert pickle.loads(pathlib.Path('old.pkl').read_bytes()) == "
            "(sniffbom.BomInfo('utf-8', 3), sniffbom.XmlGuess('utf-8', 3, 'utf-8'))",
            cwd=work,
        )
        assert upgraded.returncode == 0, upgraded.stderr

    # Run from an empty folder so the source tree cannot shadow the install.
    result = _run(python, "-I", "-c", PROGRAM, cwd=work)
    assert result.returncode == 0, result.stderr
    assert result.stdout.decode().strip() == "e2e ok"

    marked = work / "marked.txt"
    marked.write_bytes(b"\xef\xbb\xbfhi")
    script = bindir / ("sniffbom.exe" if sys.platform == "win32" else "sniffbom")
    commands: list[list[str | Path]] = [[python, "-m", "sniffbom"]]
    if os.environ.get("SNIFFBOM_E2E_NO_SCRIPT") != "1":
        commands.append([script])
    for command in commands:
        shown = _run(*command, "--json", "-", cwd=work, stdin=b"\xff\xfeh\x00")
        assert shown.returncode == 0, shown.stderr
        expected = {"path": "-", "encoding": "utf-16-le", "length": 2, "stripped": False}
        assert json.loads(shown.stdout) == [expected]
        checked = _run(*command, "--check", marked, cwd=work)
        assert checked.returncode == 1 and b"utf-8 (3 bytes)" in checked.stdout
        ignored = _run(*command, "--check", "--among", "utf-16-le", marked, cwd=work)
        assert ignored.returncode == 0 and b": none" in ignored.stdout
        piped = _run(*command, "--strip", "--json", "-", stdin=b"\xef\xbb\xbfhi", cwd=work)
        assert piped.returncode == 0 and piped.stdout == b"hi"
        assert json.loads(piped.stderr)[0]["stripped"] is True
        missing = _run(*command, work / "missing", cwd=work)
        assert missing.returncode == 2 and b"sniffbom:" in missing.stderr
        assert _run(*command, "--help", cwd=work).returncode == 0
        for mode in ([], ["--check"], ["--strip"]):
            for prefix in (b"", b"\xef\xbb\xbf"):
                paths = [work / "\U0001f680.txt", work / "second.txt"]
                for path in paths:
                    path.write_bytes(prefix + b"hello")
                redirected = _run(
                    *command,
                    *mode,
                    *paths,
                    cwd=work,
                    env={**os.environ, "PYTHONIOENCODING": "cp1252:strict"},
                )
                expected_status = 1 if mode == ["--check"] and prefix else 0
                assert redirected.returncode == expected_status, redirected.stderr
                assert redirected.stderr == b""
                assert len(redirected.stdout.splitlines()) == 2
                assert b"\\U0001f680.txt" in redirected.stdout
                expected_data = b"hello" if mode == ["--strip"] else prefix + b"hello"
                assert all(path.read_bytes() == expected_data for path in paths)
    stripped = _run(commands[-1][0], *commands[-1][1:], "--strip", marked, cwd=work)
    assert stripped.returncode == 0, stripped.stderr
    assert marked.read_bytes() == b"hi"
