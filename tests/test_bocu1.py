"""BOCU-1 state preservation, checked with actual ICU conversions when available."""

from __future__ import annotations

import ctypes
import io
import json
import os
import sys
from pathlib import Path

import pytest

from sniffbom import strip
from sniffbom._cli import main


def _convert(data: bytes, source: bytes, target: bytes) -> bytes:
    # ICU's conversion API: https://unicode-org.github.io/icu-docs/apidoc/released/icu4c/ucnv_8h.html
    library = os.environ.get("SNIFFBOM_ICU", "icu.dll" if sys.platform == "win32" else "")
    if not library:
        pytest.skip("set SNIFFBOM_ICU to a library exporting ucnv_convert")
    try:
        convert = ctypes.CDLL(library).ucnv_convert
    except (OSError, AttributeError):
        if "SNIFFBOM_ICU" in os.environ:
            raise
        pytest.skip("ICU conversion API is unavailable")
    convert.argtypes = [
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_void_p,
        ctypes.c_int32,
        ctypes.c_char_p,
        ctypes.c_int32,
        ctypes.POINTER(ctypes.c_int32),
    ]
    convert.restype = ctypes.c_int32
    output = ctypes.create_string_buffer(max(64, len(data) * 4))
    error = ctypes.c_int32(0)
    count = convert(target, source, output, len(output), data, len(data), ctypes.byref(error))
    assert error.value <= 0
    assert 0 <= count < len(output)
    return output.raw[:count]


@pytest.mark.parametrize("raw", [bytes.fromhex("fbee28cf"), bytes.fromhex("fbee28241e32")])
def test_bocu1_strip_refuses_to_discard_decoder_state(raw: bytes) -> None:
    # Handwritten regression inputs, independently decoded by ICU below.
    assert strip(raw) == raw


@pytest.mark.parametrize("text", ["\ufeff", "\ufeff\ufeff", "\ufeffA", "\ufeff\u4e00\U0001f680"])
def test_bocu1_api_preserves_independently_decoded_text(text: str) -> None:
    raw = _convert(text.encode(), b"UTF-8", b"BOCU-1")
    assert _convert(strip(raw), b"BOCU-1", b"UTF-8").decode() == text


@pytest.mark.parametrize("stdin", [False, True])
def test_bocu1_cli_preserves_independently_decoded_text(
    stdin: bool, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    text = "\ufeff\ufeffA"
    raw = _convert(text.encode(), b"UTF-8", b"BOCU-1")
    path = tmp_path / "bocu1.txt"
    path.write_bytes(raw)
    source = io.TextIOWrapper(io.BytesIO(raw))
    output = io.TextIOWrapper(io.BytesIO())
    report = io.StringIO()
    monkeypatch.setattr(sys, "stdin", source)
    monkeypatch.setattr(sys, "stdout", output if stdin else report)
    monkeypatch.setattr(sys, "stderr", report)
    assert main(["--strip", "--json", "-" if stdin else str(path)]) == 0
    result = output.buffer.getvalue() if stdin else path.read_bytes()
    assert _convert(result, b"BOCU-1", b"UTF-8").decode() == text
    assert result == raw
    assert json.loads(report.getvalue())[0]["stripped"] is False
