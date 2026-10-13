# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
