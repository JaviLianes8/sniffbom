# sniffbom 1.0.0 certification report

Progress:
- [x] Resume release/1.0.0 from main 5d4bfdd, preserving unfinished changes
- [x] PyPI checked live: 0.2.0, Python >=3.10 (2026-11-01)
- [x] API, typing, input errors, docstrings and contracts (items 1 to 6)
- [x] Eleven reference files fetched and hash-checked (item 7)
- [x] Seeded properties and large UTF-7 runs (item 9)
- [x] README, GUIDE, dated CHANGELOG and stable metadata (items 11 to 13)
- [ ] Installed wheel, PyPI upgrade and artifact inspection (items 8, 14)
- [ ] Available interpreter matrix (item 10)
- [ ] Mutation round (item 18)
- [ ] Final gates (item 15)
- [ ] Five QA lenses and final review (items 16, 19)
- [ ] PR, merge and publication (item 17)

## API and documentation

The fourteen names, parameter names and defaults from 0.2.0 remain stable and are
pinned in tests/test_contract_api.py. Changes concern input validation, buffer
interpretation, bounded errors, stream options, CLI diagnostics and serialisation;
each is listed in CHANGELOG 1.0.0. The guide distinguishes Python codec fallbacks
from full WHATWG legacy decoders and records stream setup consumption and UTF-7
buffering. All public names have executable examples, including attribute docstrings
for the tuple and literal aliases. README and GUIDE examples execute in the suite.

## Ground truth

Fetched live on 2026-11-01 with scripts/fetch_upstream.py. The manifest at
tests/upstream/MANIFEST.json records exact URLs, revisions, sizes, hashes and licences.
All eleven downloads matched. Copies remain outside the repository, selected through
SNIFFBOM_UPSTREAM. Tests verify the hashes before extracting tables and skip cleanly
when a copy is absent. No third-party text or corpus is shipped.

- Unicode FAQ: five standard BOMs, extracted from the fetched table.
- UTS #6, UTN #6, UTR #16: SCSU, BOCU-1 and UTF-EBCDIC signatures extracted from text.
- RFC 2152 and RFC 2045: UTF-7 derivation from the fetched modified-base64 alphabet.
- WHATWG Encoding Standard: BOM sniff table and decode algorithm from a pinned snapshot.
- XML 1.0 Fifth Edition: all Appendix F.1 marked and unmarked rows.
- Pinned Wikipedia BOM table: coverage of all eleven names, including UTF-1.
- Two pinned web-platform-tests files: BOM precedence and ignoreBOM cases.
- Python codecs run in this session: generated UTF-8/16/32, UTF-7 and GB18030 output,
  stripped and decoded through the public API. Handwritten cases are labelled as such.

## Preliminary validation

CPython 3.14.6: ruff format, ruff check and mypy --strict src tests exit 0;
pytest with fetched sources: 415 passed, 3 skipped (wheel opt-in, POSIX mode, symlinks).
Per-test timeout is 300 seconds. Scratch and pytest temporary directories stay under
the dedicated certification directory. Seeded tests generate 14,000 codec round trips
and 8,000 arbitrary byte inputs; long UTF-7 cases cover 100,000 characters.

## Pending review

No QA lens verdict or final reviewer pass has been recorded. Merge and publication
remain pending after preparation and the separate reviews.
