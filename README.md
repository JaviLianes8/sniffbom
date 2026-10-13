# sniffbom

Detect, name and strip the Unicode byte-order mark on a byte string

## Install

```
pip install sniffbom
```

## Usage

```python
from sniffbom import decode, detect, strip

raw = b"\xef\xbb\xbfhello"

info = detect(raw)
print(info.encoding, info.length)  # utf-8 3

print(strip(raw))  # b'hello'
print(decode(raw))  # 'hello'

detect(b"plain text")  # None
```

`detect` returns a `BomInfo` with the encoding name (`utf-8`, `utf-16-le`,
`utf-16-be`, `utf-32-le`, `utf-32-be`) and the mark length in bytes, or `None`
when there is no mark. `strip` removes the mark if present and leaves everything
else untouched. `decode` reads the mark, consumes it, and decodes the rest with
the implied encoding, falling back to `utf-8` (or a `default` you pass) when no
mark is found.

## Why

The standard library exposes the BOM byte sequences as `codecs.BOM_*` constants
but offers no single call that detects one, names the encoding and hands back the
content without it. `utf-8-sig` only covers UTF-8, and the usual hand-rolled
sniffers get the ordering wrong: a UTF-32-LE mark (`FF FE 00 00`) begins with the
UTF-16-LE mark (`FF FE`), so a naive check reports UTF-16. Larger options like
`w3lib.encoding.read_bom` pull in a scrapy-adjacent dependency. This is the small,
zero-dependency, typed primitive that does the three steps correctly.

## License

MIT. See [LICENSE](LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
