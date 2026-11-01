# sniffbom guide

## Choosing a rule

`detect`, `strip`, `decode`, `needs_more` and `text_stream` use the eleven names in
`ENCODINGS`. The tuple is ordered by matching precedence, with UTF-32 before UTF-16
and the five-byte UTF-7 form before its four-byte prefix. `among=None` enables all
names; an empty iterable enables none. Names are exact and case-sensitive, duplicates
are harmless, and a finite one-shot iterable is supported. Unknown names are errors
even when the input is empty. The order of `among` does not change precedence.

```python
from sniffbom import decode, detect, needs_more

data = b"\xff\xfe\x00\x00"
print(detect(data).encoding)
print(detect(data, among=("utf-16-le",)).encoding)
print(needs_more(b"\xff\xfe", among=("utf-16-le",)))
print(repr(decode(b"\xef\xbb\xbfhi", among=())))
# utf-32-le
# utf-16-le
# False
# '\ufeffhi'
```

`bom_sniff` returns the WHATWG names `UTF-8`, `UTF-16BE`, `UTF-16LE`, or `None`.
`whatwg_decode` applies that BOM precedence, skips one mark and uses Python codecs
with replacement. Its fallback is a Python text codec name, not a WHATWG label;
legacy decoding and label aliases can differ from a browser. In particular Python's
`latin-1` preserves U+0080, while the browser label selects Windows-1252.

`xml_autodetect` classifies a complete prefix or entity using XML 1.0 Appendix F.1.
It does not parse the declaration or validate XML. `XmlGuess.codec=None` means the
family is insufficient or no Python codec is provided. Unmarked UCS-4 requires its
declaration, so it has no codec even for the usual byte orders. Unmatched input is
`XmlGuess("other", 0, "utf-8")`. Short input is treated as final, not as a partial read.

## Bytes and results

The byte-input functions accept `bytes`, `bytearray` and `memoryview`. Views are read
as raw bytes in logical C order, irrespective of item width or shape, including
strided views. Released views raise `ValueError`. Mutable buffers are not modified;
callers must avoid concurrent mutation. `strip` always returns `bytes`.

`BomInfo(encoding, length)` and `XmlGuess(family, bom_length, codec)` are frozen,
hashable value records. Their constructors store the supplied fields without runtime
validation. `BomInfo.codec` maps known names to a Python codec, or returns `None`
for unsupported or unknown names. `WhatwgEncoding` and `XmlFamily` are literal type
aliases, not runtime validators. `__version__` is release metadata outside `__all__`.

Only a leading mark counts. Exactly one mark is removed, so a second encoded U+FEFF
is retained. UTF-7 shares the mark's last byte with the next character: use `strip`,
not `data[info.length:]`. A valid base64 run is re-encoded without its first U+FEFF;
a run with invalid padding bits stays unchanged. Detecting a signature does not
prove that the remaining bytes are valid text.

## Streams

`text_stream(binary, default="utf-8", *, errors="strict", among=None, newline=None)`
returns an `io.TextIOWrapper`. The binary reader must implement `read(size)` returning
at most that many bytes (`b""` for EOF), and `close()`. It need not seek. Closing the
wrapper closes the reader. Sniffing reads at most five bytes; UTF-7 then decodes one
character, which can buffer beyond that prefix. Newline handling follows
`io.TextIOWrapper`: `None`, `""`, `"\n"`, `"\r"`, `"\r\n"` are accepted.

```python
import io
from sniffbom import text_stream

raw = io.BytesIO(b"\xef\xbb\xbfa\r\nb")
with text_stream(raw, newline="") as text:
    print(repr(text.read()))
print(raw.closed)
# 'a\r\nb'
# True
```

This is a blocking-stream interface. `None` before the mark is decided raises
`BlockingIOError`. On setup failure, already-read bytes are not restored. Do not
retry setup on the same partially consumed reader; buffer externally if necessary.
For sockets pass `sock.makefile("rb")`. An empty `among` bypasses sniffing entirely.

## Errors

| Condition | Exception |
| --- | --- |
| Wrong byte-input type, wrong `among` container or non-string item | `TypeError` |
| Unknown `among` name | `ValueError` |
| UTF-1, UTF-EBCDIC, SCSU or BOCU-1 passed to a decoder | `UnsupportedBomError`, a `LookupError` with `.encoding` |
| Unknown codec or error handler | `LookupError` |
| Non-string codec/error handler | `TypeError` |
| NUL inside a codec/error-handler name | `ValueError` |
| Invalid newline type or value | `TypeError` or `ValueError` |
| Invalid encoded text with strict decoding | `UnicodeDecodeError` |
| Undecided non-blocking stream | `BlockingIOError` |

Lookup and validation messages do not quote supplied option values. Standard Python
codec errors retain their usual typed attributes, including the input bytes in
`UnicodeDecodeError.object`. Custom registered codecs, error handlers and readers
can raise their own exceptions. Fallbacks must be text codecs; binary transforms
such as `base64_codec` are not supported. A mark overrides the unused default or
fallback. `errors` is validated even for empty or already-valid text.

## Command line

`sniffbom FILE...` and `python -m sniffbom FILE...` name each file's signature.
`--check` returns 1 if any mark is found; `--strip` removes a mark in place;
`--json` emits one array with `path`, `encoding`, `length`, `stripped` fields.
`--among utf-8,utf-16-le` limits matching. Empty comma-separated items are ignored.
Use `--` before a path beginning with a dash. `-` reads stdin; when stripping stdin,
the bytes go to stdout and reports to stderr. Other errors return 2 and processing
continues with later paths. File contents are never included in diagnostics.
Usage errors omit supplied arguments. Error paths longer than 240 characters or
containing control characters are replaced by a placeholder; OS messages are capped
at 160 characters. Binary transform codecs are refused even on empty input.

Stripping writes beside the target and replaces it, following a symlink. File mode
is retained, but timestamps, hard-link identity and other metadata are not promised.
Read-only targets may be replaceable on POSIX and refused on Windows. No durability
guarantee is made across power loss. Malformed UTF-7 runs stay unchanged and are not
reported as stripped.

## Upgrading from 0.2.0

Install normally with `pip install --upgrade sniffbom`. Public names, signatures and
defaults remain stable. The stricter option validation, raw-buffer interpretation,
bounded errors, public class module names and exception pickle repair are listed in
the [changelog](https://github.com/JaviLianes8/sniffbom/blob/main/CHANGELOG.md).
Calls that previously relied on integer/list conversion to bytes, a bare `among`
string, invalid error handlers going unnoticed, or leaked private names must change.
Result pickles written by 0.2.0 remain readable; private imports are not supported API.
