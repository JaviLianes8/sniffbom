# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-11-01

### Stable

- The fourteen public names, parameter names and defaults from 0.2.0: signature
  detection, stripping, decoding, streaming, WHATWG BOM selection and XML families.
- Python 3.10 through 3.14, including typed results and a dependency-free CLI.

### Changed

- Surrogate-containing error-policy names now raise bounded `LookupError` before
  registry lookup, including on empty or valid input and for string subclasses.
  Exception messages, representations and arguments do not retain the supplied name.
- Decoder codec names and error-policy strings now use the underlying plain string
  value for validation and decoding. String subclass overrides cannot bypass GB18030,
  IDNA or Punycode policy restrictions, hide surrogate or NUL characters, or cause
  supported policies to be rejected. Detected marks still override unused fallbacks.
- BOCU-1 stripping now leaves the entire input unchanged, including through the CLI,
  because removing its signature would corrupt the retained decoder state. Reports
  keep `stripped=false` for these inputs.
- UTF-7 streams reject shifted runs longer than 65536 base64 bytes with a bounded
  `UnicodeError`, during setup or reading, to bound incremental decoder work.
  Bulk `decode` and `strip` retain their unrestricted run lengths.
- GB18030 streams reject `surrogateescape` with a bounded `LookupError` because
  Python's incremental decoder can leave text buffered after EOF. Bulk decoding
  and other stream error policies remain available.
- Surrogate-containing codec names raise bounded `LookupError`. The built-in
  `undefined` codec, non-strict IDNA and unsupported Punycode error policies also
  raise bounded `LookupError`.
  Fallback documentation now requires replacement compatibility and describes
  propagated built-in codec errors.
- Streams reject readers lacking callable `read` or `close` with bounded `TypeError`
  before consuming input, including when `among` is empty.
- `UnsupportedBomError` normalizes string subclasses to plain strings for its
  `.encoding` attribute and uses only canonical names in its redacted message.
- CLI reports escape characters unsupported by the output encoding, preserving
  exit statuses and processing all paths when output is redirected.
- Byte inputs consistently reject integers and integer iterables with `TypeError`;
  only `bytes`, `bytearray` and `memoryview` are accepted. Buffer contents are used
  directly, including wide-item and multidimensional views and bytes subclasses.
- Invalid `among` entries raise `TypeError` for non-strings and `ValueError` for
  unknown names, without quoting input. Bare bytearrays and memoryviews are rejected
  as collections of names. Streams validate `among` even when it is empty or a string.
- Decoder codec names and error handlers are checked even on empty or valid input.
  Unknown names raise a bounded `LookupError`; embedded NUL raises a bounded
  `ValueError`. A detected mark still takes precedence over an unused default.
- Binary transform codecs are rejected with `LookupError`, including on empty input.
- Streams validate newline values before reading; invalid values raise bounded
  `TypeError` or `ValueError` messages.
- Public result and exception classes identify their module as `sniffbom` for new
  pickles. Old result pickles remain readable. `UnsupportedBomError` now preserves
  its encoding across copying and pickling, bounds its message and rejects non-strings.
- Removed the accidental top-level `annotations` attribute from the public namespace.
- CLI usage errors no longer echo arbitrary arguments; path errors are bounded and
  invalid paths return status 2. Replacement files use a short fixed prefix.

### Added

- Regression contracts distinguish composed and decomposed registered error-handler
  names and reject adjacent surrogate pairs in codec and error-policy names with
  exact bounded errors. Coverage includes string subclasses, marked/unmarked input
  and both decoding APIs, plus WHATWG fallback validation and mark precedence.
- Regression contracts for registered error-handler names containing U+D7FF and
  U+E000, and bounded surrogate rejection at every position in error-policy names,
  through bulk and streaming decoding with marked input and string subclasses.
- Runnable API examples, a guide with upgrade notes, complete input contracts,
  seeded properties, source provenance checks and installed-wheel upgrade coverage.

## [0.2.0]

### Added

- Signatures of UTF-7, UTF-1, UTF-EBCDIC, SCSU, BOCU-1 and GB18030, `ENCODINGS` and the
  `BomInfo.codec` property.
- `among=` on `detect`, `strip` and `decode` to choose which marks count, for the WHATWG
  reading of `FF FE 00 00` or a `TextDecoder` that strips only its own mark.
- `errors=` on `decode`, and `UnsupportedBomError` for a mark Python cannot decode.
- `needs_more` and `text_stream` for streams and partial reads.
- `bom_sniff` and `whatwg_decode`, after the WHATWG Encoding Standard.
- `xml_autodetect` and `XmlGuess`, after XML 1.0 Appendix F.1.
- The `sniffbom` command line (`--check`, `--strip`, `--json`, `--among`) and
  `python -m sniffbom`.

### Changed

- `strip` removes a UTF-7 mark exactly, re-encoding the rest of its base64 run, and
  leaves a malformed run as it is.
- Every function accepts `bytearray` and `memoryview` as well as `bytes`.

## [0.1.0]

- First release: `detect`, `strip`, `decode` and the `BomInfo` result, covering
  UTF-8, UTF-16 and UTF-32 marks in both byte orders.
