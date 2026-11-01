"""Compare Unicode decoding with Node.js TextDecoder, when explicitly enabled."""

from __future__ import annotations

import json
import os
import random
import subprocess

import pytest

from sniffbom import whatwg_decode

NODE = os.environ.get("SNIFFBOM_NODE")
pytestmark = pytest.mark.skipif(NODE is None, reason="set SNIFFBOM_NODE for TextDecoder oracle")

PROGRAM = """
const fs = require('node:fs');
const cases = JSON.parse(fs.readFileSync(0, 'utf8'));
const result = cases.map(([bytes, fallback]) => {
  let label = fallback;
  if (bytes[0] === 239 && bytes[1] === 187 && bytes[2] === 191) label = 'utf-8';
  else if (bytes[0] === 254 && bytes[1] === 255) label = 'utf-16be';
  else if (bytes[0] === 255 && bytes[1] === 254) label = 'utf-16le';
  return new TextDecoder(label).decode(Uint8Array.from(bytes));
});
process.stdout.write(JSON.stringify(result));
"""


def test_seeded_unicode_decoding_matches_textdecoder() -> None:
    assert NODE is not None
    rng = random.Random(20261101)
    cases: list[tuple[list[int], str]] = []
    expected: list[str] = []
    for fallback in ("utf-8", "utf-16le", "utf-16be"):
        for _ in range(2000):
            mark = rng.choice([b"", b"\xef\xbb\xbf", b"\xff\xfe", b"\xfe\xff"])
            data = mark + rng.randbytes(rng.randrange(80))
            cases.append((list(data), fallback))
            expected.append(whatwg_decode(data, fallback))
    result = subprocess.run(
        [NODE, "-e", PROGRAM],
        input=json.dumps(cases).encode(),
        capture_output=True,
        timeout=60,
        check=True,
    )
    assert json.loads(result.stdout) == expected
