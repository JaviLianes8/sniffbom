# sniffbom improvement round

Progress:
- [x] Brainstorm ranked improvements (this file)
- [x] Pin the ground truth: Unicode BOM FAQ, UTS #6, UTN #6, UTR #16, RFC 2152, WHATWG Encoding, XML 1.0 Appendix F, web-platform-tests
- [x] Full signature table with codecs, `among` filter and the UTF-16LE / UTF-32LE rule
- [x] UTF-7 marks: detection, exact stripping, decoding
- [x] Streams and partial reads: `needs_more`, `text_stream`
- [x] WHATWG `bom_sniff` and `whatwg_decode`
- [x] XML 1.0 Appendix F `xml_autodetect`
- [x] Command line
- [x] Contracts: pinned sources, web-platform-tests cases, README examples, installed wheel
- [x] Docs and packaging: README, CHANGELOG, metadata, sdist contents
- [x] Gates: ruff format, ruff check, mypy --strict, pytest
- [x] Mutation run: removing guarded logic makes the suite fail
- [ ] Independent review findings fixed with regression tests
- [ ] Pull request opened, guard clean

## Starting point

`0.1.0` gives `detect`, `strip`, `decode` and a frozen `BomInfo` for the five marks of the
Unicode FAQ table. Probed against the sources below:

- The signatures of the other encoding schemes are not recognised: UTF-7 (`+/v` and one of
  `8 9 + /`), UTF-1 (`F7 64 4C`), UTF-EBCDIC (`DD 73 66 73`), SCSU (`0E FE FF`), BOCU-1
  (`FB EE 28`) and GB18030 (`84 31 95 33`). `decode(b"\x84\x31\x95\x33hi")` raises a
  `UnicodeDecodeError` from the UTF-8 fallback instead of reading GB18030.
- `decode` with a `default` that has its own mark keeps it: `decode(gb18030_bytes,
  default="gb18030")` returns text starting with U+FEFF.
- `FF FE 00 00` is always UTF-32LE. That is what the Unicode table says, but the WHATWG
  Encoding Standard never sniffs UTF-32 and reads the same bytes as UTF-16LE followed by
  NUL. A caller has no way to pick a rule, nor to say "only strip the mark of the encoding
  I already know", which is what a `TextDecoder` does.
- No help for streams: a reader that got `FF FE` so far cannot ask whether two more bytes
  could change the answer, and there is no way to wrap a binary file so the mark is gone.
- `decode` has no `errors` argument, so malformed input cannot be replaced.
- No XML entity autodetection (Appendix F), no command line.

## Sources (fetched 2026-10-13)

- Unicode FAQ on UTF and BOM, https://www.unicode.org/faq/utf_bom.html: the five marks.
- UTS #6 revision 4, https://www.unicode.org/reports/tr6/tr6-4.html, section 8.1: the
  recommended SCSU signature `0E FE FF` and the alternatives.
- UTN #6 version 2, https://www.unicode.org/notes/tn6/tn6-2.html, section 3: `FB EE 28`.
- UTR #16 revision 8, https://www.unicode.org/reports/tr16/tr16-8.html, section 3.5:
  `DD 73 66 73`.
- RFC 2152, https://www.rfc-editor.org/rfc/rfc2152.txt: modified base64, from which the
  UTF-7 form of U+FEFF follows.
- Wikipedia, Byte order mark, oldid 1377262082: the only fetched source that lists UTF-1
  (`F7 64 4C`) and GB18030 (`84 31 95 33`); the GB18030 value is also checked against the
  Python codec, the UTF-1 value has no second source.
- WHATWG Encoding Standard, commit snapshot a985b62a9b45c17da3e17a9f0a0b4e30c34c4a8a (last
  updated 21 May 2026): the "decode" and "BOM sniff" algorithms.
- XML 1.0 Fifth Edition, https://www.w3.org/TR/2008/REC-xml-20081126/, Appendix F.1.
- web-platform-tests at commit 6c99968b9aea04bc6d5f61194a200387505d41d9:
  `encoding/textdecoder-byte-order-marks.any.js` and `textdecoder-ignorebom.any.js`.
- None of these files is committed. `tests/upstream/MANIFEST.json` records URL, revision,
  size, sha256 and licence; `scripts/fetch_upstream.py` fetches and checks them into the
  ignored `tests/upstream/` folder, and their tests skip while they are absent.

## Ranked improvements

1. **Full signature table.** Eleven schemes, longest match first, each with the Python
   codec that reads it (`None` for UTF-1, UTF-EBCDIC, SCSU and BOCU-1, which Python lacks).
   `BomInfo` keeps its two fields and gains `codec`. `decode` reads a mark through its
   codec and raises `UnsupportedBomError` (a `LookupError`) for a scheme with no codec,
   instead of a confusing `UnicodeDecodeError`. `errors` is passed through, and a mark is
   kept as U+FEFF only when it is a second mark.
2. **The UTF-16LE / UTF-32LE rule, made explicit.** `among=` restricts the table to some
   encodings, so `among=("utf-8", "utf-16-le", "utf-16-be")` gives the WHATWG reading of
   `FF FE 00 00` and `among=("utf-16-le",)` strips only that mark, like a `TextDecoder`.
3. **UTF-7 done right.** The fourth byte of a UTF-7 mark carries two bits of the next
   character, so a byte slice cannot remove it. `strip` re-encodes the rest of the shift
   run so the result decodes to the original text minus U+FEFF, checked against the Python
   codec for every printable ASCII and a sample of other characters.
4. **Streams and partial reads.** `needs_more(data)` says whether more bytes could change
   the answer (`FF FE` might be UTF-32LE, `EF BB` might be UTF-8). `text_stream(binary)`
   reads only the bytes it needs, never seeks, and returns a text stream with the mark
   consumed, for files, pipes and sockets.
5. **WHATWG decode.** `bom_sniff` is the three row table of the standard; `whatwg_decode`
   is "decode": the mark wins over the fallback, three or two bytes are skipped, and
   errors become U+FFFD.
6. **XML 1.0 Appendix F.** `xml_autodetect` returns the family of the first four bytes,
   with and without a mark, including the unusual UCS-4 orders and EBCDIC, the mark
   length and a codec where the family alone decides it.
7. **Command line.** `sniffbom FILE...` names the mark of each file, `--check` exits 1 when
   any has one (a pre-commit lint), `--strip` removes it in place, `--json` for scripts.
   It fits: finding and removing stray marks is a shell task.
8. **Contracts.** Every table value is read back from the pinned sources; the WHATWG and
   XML tables are parsed from the specification text; the web-platform-tests cases run
   through `decode` with `among`; README examples run; the installed wheel and its console
   script are driven from an empty folder.
9. **Docs and packaging.** README with executed examples and an API table, CHANGELOG,
   keywords and classifiers, an sdist without planning notes or fetched files.

## Out of scope

- Guessing encodings from content (statistics, `chardet` style): this is a mark reader.
- Codecs for UTF-1, UTF-EBCDIC, SCSU and BOCU-1: they are recognised and named, not decoded.
- Reading the XML encoding declaration itself: Appendix F only names the family.

## Mutation run

43 hand-written mutants over every module (table rows and marks, `among` checks, the
`needs_more` bound, the UTF-7 re-encoding, codec errors, stream head handling and close,
WHATWG rows and replacement, Appendix F rows, command line exit codes, rewrite and
parsing): all 43 make the suite fail, with the reference files fetched. The run writes no
bytecode, purges `__pycache__` before each mutant, treats a hang as a failure, and checks
that the unmutated suite is green before and after.
