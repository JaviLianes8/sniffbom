"""Seeded generated cases, checked against Python codecs and a signature oracle."""

from __future__ import annotations

import io
import random
from contextlib import suppress

import pytest
from test_bom import CASES, ROUND_TRIP

from sniffbom import (
    BomInfo,
    UnsupportedBomError,
    bom_sniff,
    decode,
    detect,
    needs_more,
    strip,
    text_stream,
    whatwg_decode,
    xml_autodetect,
)


@pytest.mark.parametrize("seed", [2152, 20261101])
def test_generated_unicode_round_trips_match_python_codecs(seed: int) -> None:
    rng = random.Random(seed)
    for _ in range(1000):
        text = "".join(
            chr(rng.choice([rng.randrange(0xD800), rng.randrange(0xE000, 0x110000)]))
            for _ in range(rng.randrange(24))
        )
        for codec in ROUND_TRIP:
            data = ("\ufeff" + text).encode(codec)
            assert decode(data) == text
            assert strip(data).decode(codec) == text
            with text_stream(io.BytesIO(data), newline="") as stream:
                assert stream.read() == text


@pytest.mark.parametrize("seed", [42, 935])
def test_arbitrary_bytes_match_signature_oracle_and_do_not_crash(seed: int) -> None:
    rng = random.Random(seed)
    ordered = sorted(CASES, key=lambda case: -len(case[0]))
    for _ in range(4000):
        prefix = rng.choice(CASES)[0] if rng.randrange(2) else b""
        data = prefix + rng.randbytes(rng.randrange(80))
        match = next((case for case in ordered if data.startswith(case[0])), None)
        expected = None if match is None else BomInfo(match[1], match[2])
        assert detect(data) == expected
        assert needs_more(data) == any(
            len(data) < len(mark) and mark.startswith(data) for mark, _, _ in CASES
        )
        stripped = strip(data)
        assert len(stripped) <= len(data)
        assert isinstance(bom_sniff(data), (str, type(None)))
        assert isinstance(whatwg_decode(data), str)
        assert xml_autodetect(data).bom_length <= len(data)
        if expected is not None and expected.encoding != "utf-7":
            assert stripped == data[expected.length :]
        with suppress(UnicodeDecodeError, UnsupportedBomError):
            decode(data)


def test_every_signature_prefix_has_the_expected_partial_read_state() -> None:
    for mark, _, _ in CASES:
        for count in range(len(mark) + 1):
            prefix = mark[:count]
            assert needs_more(prefix) == any(
                len(prefix) < len(other) and other.startswith(prefix) for other, _, _ in CASES
            )
            if not needs_more(prefix):
                for byte in range(256):
                    assert detect(prefix + bytes([byte])) == detect(prefix)


def test_large_valid_and_malformed_utf7_runs_are_bounded_and_exact() -> None:
    text = "\u8000" * 100000
    data = ("\ufeff" + text).encode("utf-7")
    assert strip(data).decode("utf-7") == text
    assert decode(data) == text
    assert strip(b"+/v9" + b"A" * 100000 + b"/") == b"+/v9" + b"A" * 100000 + b"/"
