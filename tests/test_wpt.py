"""web-platform-tests encoding cases, run through `decode` with ``among``.

`TextDecoder(label)` strips only the mark of its own encoding, which is
``decode(data, codec, among=(codec,))``; ``ignoreBOM: true`` is ``among=()``. The files
are read from tests/upstream and the tests skip until they are fetched.
"""

from __future__ import annotations

import re

from conftest import read_upstream

from sniffbom import decode, whatwg_decode

CODECS = {"utf-8": "utf-8", "utf-16le": "utf-16-le", "utf-16be": "utf-16-be"}


def _numbers(text: str) -> bytes:
    return bytes(int(value, 16) for value in re.findall(r"0x([0-9A-Fa-f]{2})", text))


def _js_string(literal: str) -> str:
    # The JS literal spells astral characters as surrogate pairs; join them.
    raw = literal.encode("ascii").decode("unicode_escape")
    return raw.encode("utf-16-le", "surrogatepass").decode("utf-16-le")


def test_byte_order_marks() -> None:
    source = read_upstream("wpt/textdecoder-byte-order-marks.any.js")
    cases = re.findall(r"encoding: '([\w-]+)',\s*bom: \[([^\]]*)\],\s*bytes: \[([^\]]*)\]", source)
    assert len(cases) == 3
    literal = re.search(r"var string = '([^']*)'", source)
    assert literal is not None
    expected = _js_string(literal.group(1))
    for label, bom, body in cases:
        codec = CODECS[label]
        mine = (codec,)
        assert decode(_numbers(body), codec, among=mine) == expected
        assert decode(_numbers(bom) + _numbers(body), codec, among=mine) == expected
        assert decode(_numbers(bom) + _numbers(body)) == expected
        assert whatwg_decode(_numbers(bom) + _numbers(body), "latin-1") == expected
        for other_label, other_bom, _ in cases:
            if other_label != label:
                garbled = decode(
                    _numbers(other_bom) + _numbers(body), codec, among=mine, errors="replace"
                )
                assert garbled != expected


def test_ignore_bom() -> None:
    source = read_upstream("wpt/textdecoder-ignorebom.any.js")
    cases = re.findall(r"\{encoding: '([\w-]+)', bytes: \[([^\]]*)\]\}", source)
    assert len(cases) == 3
    assert "BOM + 'abc'" in source
    for label, body in cases:
        codec = CODECS[label]
        assert decode(_numbers(body), codec, among=()) == "\ufeffabc"
        assert decode(_numbers(body), codec, among=(codec,)) == "abc"
        assert decode(_numbers(body), codec) == "abc"
