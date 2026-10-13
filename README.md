# sniffbom

Detect, name and strip the Unicode byte-order mark on a byte string: every signature in
use (UTF-8, UTF-16 and UTF-32 in both orders, UTF-7, UTF-1, UTF-EBCDIC, SCSU, BOCU-1 and
GB18030), streams and partial reads, the WHATWG decode rule and XML entity autodetection.
Zero dependencies, fully typed; every function takes `bytes`, `bytearray` or
`memoryview`.

## Install

```
pip install sniffbom
```

## Usage

Every example below runs in the test suite, and each comment is exactly what it prints.

```python
from sniffbom import decode, detect, strip

raw = b"\xef\xbb\xbfhello"
info = detect(raw)
print(info.encoding, info.length, info.codec)
print(strip(raw))
print(decode(raw))
print(detect(b"plain text"))
# utf-8 3 utf-8
# b'hello'
# hello
# None
```

`decode` reads the mark through its codec and consumes it; without a mark it uses
`default` (`utf-8` unless you pass another). Only one mark is removed, a second one stays
as U+FEFF. `errors` goes to the codec.

```python
from sniffbom import UnsupportedBomError, decode, detect

print(decode(b"\x84\x31\x95\x33caf\xa8\xa6"))
print(decode(b"+/v8A6Q-"))
print(decode(b"\xef\xbb\xbfa\xff", errors="replace") == "a\ufffd")
try:
    decode(b"\x0e\xfe\xffhi")
except UnsupportedBomError as error:
    print(error.encoding, isinstance(error, LookupError))
# café
# é
# True
# scsu True
```

UTF-1, UTF-EBCDIC, SCSU and BOCU-1 are recognised and named, but Python has no codec for
them, so `decode` raises `UnsupportedBomError` and `BomInfo.codec` is `None`.

### Which rule reads `FF FE 00 00`?

The Unicode table reads it as a UTF-32LE mark; the WHATWG Encoding Standard never sniffs
UTF-32 and reads UTF-16LE followed by NUL. `detect` follows the Unicode table and
`among` picks the rule. `among` also says "only the mark of the encoding I already know",
which is what a `TextDecoder` does.

```python
from sniffbom import bom_sniff, decode, detect, whatwg_decode

data = b"\xff\xfe\x00\x00"
print(detect(data).encoding)
print(detect(data, among=("utf-8", "utf-16-le", "utf-16-be")).encoding)
print(bom_sniff(data), repr(whatwg_decode(data)))
print(repr(decode(b"\xef\xbb\xbfabc", among=())))
# utf-32-le
# utf-16-le
# UTF-16LE '\x00'
# '\ufeffabc'
```

`whatwg_decode(data, fallback)` is the "decode" algorithm: the mark wins over the
fallback encoding and malformed input becomes U+FFFD instead of raising.

### Streams and partial reads

```python
import io

from sniffbom import needs_more, text_stream

print(needs_more(b"\xff\xfe"), needs_more(b"\xff\xfeh"))
stream = text_stream(io.BytesIO(b"\xff\xfeh\x00i\x00"))
print(stream.read())
# True False
# hi
```

`needs_more` says whether more bytes could change the answer (`FF FE` may still become a
UTF-32LE mark). `text_stream` reads at most five bytes to decide, never seeks, and
returns a text stream with the mark consumed, so it works on pipes and on sockets through
`sock.makefile("rb")`. A non-blocking stream that has no data before the mark is decided
raises `BlockingIOError` rather than guessing.

### XML entities

```python
from sniffbom import xml_autodetect

print(xml_autodetect(b"\xfe\xff\x00<\x00?"))
print(xml_autodetect(b"<?xml version='1.0'?>").family)
# XmlGuess(family='utf-16-be', bom_length=2, codec='utf-16-be')
# ascii
```

`xml_autodetect` follows XML 1.0 Appendix F.1: it names the family of the first four
bytes, with or without a mark, including the unusual UCS-4 orders and EBCDIC. `codec` is
set when the family alone decides the encoding and is `None` when the encoding
declaration must be read.

## Command line

```
sniffbom FILE...              # name the mark of each file
sniffbom --check FILE...      # exit 1 if any file has a mark
sniffbom --strip FILE...      # remove the mark in place; - reads stdin, writes stdout
sniffbom --json FILE...       # one JSON array
sniffbom --among utf-8 FILE   # only look for some marks
```

Exit status: 0 when done, 1 when `--check` finds a mark, 2 on a usage or read error.
`--strip` writes the new content next to the file and swaps it in (following a symlink to
its target, keeping the mode); a malformed UTF-7 run it cannot shorten exactly is left as
it is. When stdin is stripped to stdout, the report goes to stderr.

## API

| Name | What it does |
| --- | --- |
| `detect(data, *, among=None)` | The leading mark as a `BomInfo`, or `None` |
| `strip(data, *, among=None)` | `data` without one leading mark, exact for UTF-7 too |
| `decode(data, default="utf-8", *, errors="strict", among=None)` | Text with the mark consumed |
| `needs_more(data, *, among=None)` | Whether more bytes could change `detect` |
| `text_stream(binary, default="utf-8", *, errors, among, newline)` | A text stream without the mark |
| `bom_sniff(data)` | The WHATWG "BOM sniff": `"UTF-8"`, `"UTF-16BE"`, `"UTF-16LE"` or `None` |
| `whatwg_decode(data, fallback="utf-8")` | The WHATWG "decode" algorithm |
| `xml_autodetect(data)` | An `XmlGuess` after XML 1.0 Appendix F.1 |
| `BomInfo` | `encoding`, `length` and the `codec` property |
| `XmlGuess` | `family`, `bom_length`, `codec` |
| `XmlFamily`, `WhatwgEncoding` | The literal types of those names |
| `ENCODINGS` | Every name `detect` reports, in the order the marks are tried |
| `UnsupportedBomError` | A `LookupError` for a mark Python cannot decode |

A UTF-7 mark is `+/v` and a fourth byte (`8`, `9`, `+` or `/`) that also carries two bits
of the next character, so slicing `data[info.length:]` is only exact for `+/v8-`; `strip`
re-encodes the rest of the run and is always exact. Text that happens to start with
`+/v8` is read as UTF-7, as with any signature.

## Why

The standard library exposes the BOM byte sequences as `codecs.BOM_*` constants but
offers no single call that detects one, names the encoding and hands back the content
without it. `utf-8-sig` only covers UTF-8, and the usual hand-rolled sniffers get the
ordering wrong: a UTF-32-LE mark (`FF FE 00 00`) begins with the UTF-16-LE mark
(`FF FE`), so a naive check reports UTF-16. Larger options pull in dependencies. This is
the small, typed primitive that does those steps correctly and says which rule it uses.

## Sources

The tables are checked against the Unicode BOM FAQ, UTS #6 (SCSU), UTN #6 (BOCU-1),
UTR #16 (UTF-EBCDIC), RFC 2152 (UTF-7), the WHATWG Encoding Standard, XML 1.0 Appendix F
and web-platform-tests. `python scripts/fetch_upstream.py` fetches them into
`tests/upstream/` (they are not part of the repository) and their tests run once they are
there.

## License

MIT. See [LICENSE](LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
