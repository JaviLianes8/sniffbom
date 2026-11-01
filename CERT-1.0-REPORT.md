# sniffbom 1.0.0 certification report

Preparation completed on 2026-11-01. PyPI serves 0.2.0, whose nine Python modules
match main at 5d4bfdd2250a3fa2ba20d50032d7f764dcb8f524 byte for byte.

Progress:
- [x] Stable API, public surface, examples, types and errors (items 1 to 5)
- [x] Complete contracts and fetched ground truth (items 6, 7)
- [x] Built-wheel consumer, CLI and live PyPI upgrade (item 8)
- [x] Seeded properties, reference comparison and scaling (item 9)
- [x] Available interpreters and all supported minor versions (item 10)
- [x] README, GUIDE, CHANGELOG and stable metadata (items 11 to 13)
- [x] Wheel and sdist inspection (item 14)
- [x] Four gates, plus strict typing of tests (item 15)
- [x] Twenty-four deliberate mutations caught (item 18)
- [ ] Independent reviewer (item 16)
- [ ] Five QA lenses (item 19)
- [ ] Merge and publication (item 17)

## Scorecard

| Item | Result | Evidence |
| --- | --- | --- |
| 1 | PASS | All fourteen public names, parameter names and defaults retained from 0.2.0; signatures pinned; every behaviour change in CHANGELOG |
| 2 | PASS | Exact __all__, no accidental public attributes; examples use public imports |
| 3 | PASS | Fifteen executable API docstrings, including tuple/type-alias attribute docs and the codec property; README and GUIDE examples executed |
| 4 | PASS | mypy --strict src tests; py.typed in wheel; strict external consumer checked against installed wheel |
| 5 | PASS | Typed built-in errors and UnsupportedBomError; bounded lookup, option and CLI diagnostics; GUIDE error table |
| 6 | PASS | Contracts cover every public name, type, field, default, input restriction, streaming ownership, serialisation and CLI exit status |
| 7 | PASS | Eleven live-fetched references checked by hash; Node.js and Python codecs run as independent references |
| 8 | PASS | Fresh venv, installed wheel, both CLI entry points by subprocess, live 0.2.0 upgraded in place and old result pickles loaded |
| 9 | PASS | 14,000 codec round trips, 8,000 arbitrary byte cases, 6,000 Node.js comparisons, five scaling dimensions |
| 10 | PASS | Seven distinct interpreter builds covering 3.10 to 3.14 and free-threaded 3.14 |
| 11 | PASS | Absolute README links, problem and honest alternatives, guide and changelog, exact certification badge; twine check --strict |
| 12 | PASS | CHANGELOG 1.0.0 dated 2026-11-01 |
| 13 | PASS | Version 1.0.0, Production/Stable, Python 3.10 to 3.14, MIT, project URLs, keywords, no runtime dependencies |
| 14 | PASS | Wheel and sdist lists inspected; LICENSE and py.typed; no fetched content, caches or certification notes in artifacts |
| 15 | PASS | Each gate exits 0 separately; full suite 417 passed, 2 platform skips |
| 16 | PENDING | No independent reviewer verdict recorded |
| 17 | PENDING | Release branch prepared; merge and publication remain pending |
| 18 | PASS | 24 isolated mutations, 24 caught, no survivors; table below |
| 19 | PENDING | No QA lens verdicts recorded |

## API review and upgrade

The public names and signatures remain stable. Changes are recorded in CHANGELOG:
consistent byte-input validation and raw-buffer interpretation; safe among errors;
validation of codec/error-handler names even on empty input; rejection of binary
transforms; stream newline validation before reading; public class module names;
UnsupportedBomError copying/pickling and bounded messages; removal of the accidental
annotations attribute; bounded CLI errors and invalid-path status 2.

BomInfo and XmlGuess remain frozen value records with unchanged field order and
unvalidated constructors. Old result pickles load after the upgrade. The GUIDE
documents UTF-7 shared bits, malformed-run preservation, stream ownership and setup
consumption, Python fallback codec semantics, and the limits of XML classification.
Standard codec exceptions retain their typed input attributes; custom codecs, readers
and handlers can raise their own errors.

## Ground truth

Fetched live on 2026-11-01 with scripts/fetch_upstream.py. The tracked manifest at
tests/upstream/MANIFEST.json records exact URLs, revisions, sizes, SHA-256 and licences.
All eleven downloads matched. Copies live outside the repository, selected through
SNIFFBOM_UPSTREAM. Tests verify the hashes before reading and skip cleanly when files
are absent. No third-party prose or corpus is committed or shipped.

- Unicode BOM FAQ: all five UTF-8/16/32 signatures extracted from the fetched table.
- UTS #6, UTN #6, UTR #16: SCSU, BOCU-1 and UTF-EBCDIC signatures extracted from text.
- RFC 2152 and RFC 2045: UTF-7 signature derivation from the fetched base64 alphabet.
- WHATWG Encoding Standard: BOM sniff table and decode steps from the pinned snapshot.
- XML 1.0 Fifth Edition: all marked and unmarked Appendix F.1 rows.
- Pinned Wikipedia BOM table: all eleven names, including historical UTF-1.
- Two pinned web-platform-tests files: BOM precedence and ignoreBOM cases.
- CPython codecs executed on generated Unicode: UTF-8/16/32, UTF-7 and GB18030.
  Handwritten tables are explicitly labelled and cross-checked against the sources.
- Node.js v24.18.0 TextDecoder executed on 2026-11-01: 6,000 seeded byte sequences
  with UTF-8/UTF-16 fallback and BOM precedence, no differences. Reference:
  [Node.js TextDecoder](https://nodejs.org/api/util.html#class-utiltextdecoder). Run through the optional
  tests/test_reference_node.py with SNIFFBOM_NODE set to the local executable.

## Packaging and real consumers

The wheel is built from the sdist, installed into fresh venvs, and imported from
site-packages with the working directory outside the repository. The installed API
and both sniffbom.exe and python -m sniffbom are driven by subprocess: JSON, checking,
selective marks, stdin stripping, file rewriting, help and missing-file status.
SNIFFBOM_E2E=1 and SNIFFBOM_E2E_PYPI=1 enable the tracked e2e test. It installs the
actual PyPI 0.2.0, checks the existing contracts, saves result pickles, upgrades to the
built wheel and checks results again. A separate fresh venv installs the sdist and
runs a consumer importing every public name plus the module CLI.

The wheel contains only the package, type marker, entry-point metadata and MIT licence.
The sdist contains source, maintained tests, the URL/hash manifest and fetch script,
README, GUIDE, CHANGELOG, CONTRIBUTING, LICENSE and build metadata. Hatchling also
includes .gitignore. Downloaded references, caches, release scripts and reports are
absent. Both artifacts pass twine check --strict. The external typed consumer passes
mypy --strict against the installed package without a source-tree import.

## Interpreter matrix

Suite from the sdist with src moved out of the import path, against the installed
wheel. Every run includes the fetched references and Node.js comparison, plus separate
module and console CLI subprocesses. Each gives 416 passed and 3 skips: the wheel
rebuild is opt-in and run separately; POSIX file-mode semantics and symlink creation
are unavailable on this Windows host.

| Interpreter | Result |
| --- | --- |
| CPython 3.14.6 | PASS |
| CPython 3.10.22 | PASS |
| CPython 3.11.18 | PASS |
| CPython 3.12.16 | PASS |
| CPython 3.13.18 | PASS |
| CPython 3.14.10t | PASS |
| CPython 3.14.10 | PASS |

At inventory time only system 3.14.6 existed; thirteen other launcher entries pointed
to removed installations. Six additional builds were installed under scratch without
changing the registry or defaults. All supported minor versions were exercised;
no supported minor version remains untested. Junction aliases resolve to the same
builds and are not counted as additional interpreter versions.

## Properties and scaling

Seeds 2152 and 20261101 generate 2,000 Unicode strings across seven Python codecs,
checked by decode, strip and text_stream. Seeds 42 and 935 generate 8,000 arbitrary
byte sequences checked against a separate signature oracle. Prefix tests cover every
signature boundary and every possible next byte after a completed prefix. UTF-7
large-run contracts use 100,000 characters. Node.js comparisons use seed 20261101.

Median elapsed milliseconds over five runs at 32,000, 128,000 and 512,000 input
units (characters, bytes or repeated names). Growth is far below quadratic in these
measured ranges; timings are evidence, not machine-dependent test thresholds.

| Case | 32,000 | 128,000 | 512,000 |
| --- | ---: | ---: | ---: |
| UTF-7 strip | 82.443 | 345.818 | 1933.814 |
| UTF-7 decode | 0.340 | 1.761 | 6.118 |
| malformed UTF-7 | 17.870 | 72.699 | 372.304 |
| strided sniff | 0.285 | 1.012 | 4.369 |
| large among | 6.425 | 27.018 | 170.661 |

## Mutation round

Runtime source matches 8a23bfa. Each mutation was applied alone in a scratch copy;
bytecode caching was disabled, the contract suite ran with -x, a 300-second per-test
timeout and a 300-second process limit, then the file was restored. The unchanged
suite passed before and after the round. All 24 mutations produced test
failures in the named tests; none survived or relied on syntax/collection errors.

| ID | Deliberate bug | Module | Caught by |
| --- | --- | --- | --- |
| M01 | UTF-8 mark changed | `_table.py` | `tests/test_bom.py::test_each_bom_is_detected_with_name_and_length[\xef\xbb\xbf-utf-8-3]` |
| M02 | UTF-32LE decoded as big endian | `_table.py` | `tests/test_bom.py::test_decode_round_trip[utf-32-le]` |
| M03 | detected length off by one | `_table.py` | `tests/test_bom.py::test_each_bom_is_detected_with_name_and_length[\xef\xbb\xbf-utf-8-3]` |
| M04 | unknown among wrong exception | `_table.py` | `tests/test_bom.py::test_among_rejects_unknown_names` |
| M05 | among filtering removed | `_table.py` | `tests/test_bom.py::test_among_reads_ff_fe_00_00_as_utf16_le` |
| M06 | complete prefix still needs more | `_table.py` | `tests/test_docstrings.py::test_guide_examples_print_the_documented_output` |
| M07 | strip retains final mark byte | `_bom.py` | `tests/test_bom.py::test_strip_removes_only_the_bom` |
| M08 | decode retains mark | `_bom.py` | `tests/test_bom.py::test_among_reads_ff_fe_00_00_as_utf16_le` |
| M09 | unsupported mark falls back to UTF-8 | `_bom.py` | `tests/test_bom.py::test_decode_refuses_schemes_python_cannot_read[\xddsfs]` |
| M10 | strip ignores UTF-7 shared bits | `_bom.py` | `tests/test_properties.py::test_generated_unicode_round_trips_match_python_codecs[2152]` |
| M11 | WHATWG uses strict errors | `_whatwg.py` | `tests/test_docstrings.py::test_docstrings_run_including_attribute_and_property_examples` |
| M12 | WHATWG leaves mark in output | `_whatwg.py` | `tests/test_contract_inputs.py::test_views_are_read_as_raw_bytes[wide]` |
| M13 | XML unmatched codec missing | `_xml.py` | `tests/test_whatwg_xml.py::test_xml_autodetect_follows_appendix_f[<root/>-expected15]` |
| M14 | XML mark length zero | `_xml.py` | `tests/test_contract_inputs.py::test_views_are_read_as_raw_bytes[wide]` |
| M15 | UTF-7 consumes wrong bit count | `_utf7.py` | `tests/test_properties.py::test_generated_unicode_round_trips_match_python_codecs[2152]` |
| M16 | UTF-7 invalid six-bit padding allowed | `_utf7.py` | `tests/test_review_fixes.py::test_a_utf7_run_with_six_spare_zero_bits_is_left_unchanged` |
| M17 | stream keeps BOM prefix | `_stream.py` | `tests/test_contract_inputs.py::test_among_generators_duplicates_and_order_do_not_change_precedence` |
| M18 | closing wrapper leaves reader open | `_stream.py` | `tests/test_docstrings.py::test_guide_examples_print_the_documented_output` |
| M19 | CLI check exits zero | `_cli.py` | `tests/test_cli.py::test_check_exits_one_when_a_mark_is_found` |
| M20 | CLI reports all files stripped | `_cli.py` | `tests/test_cli.py::test_json_report` |
| M21 | wide views sliced in items | `_buffer.py` | `tests/test_contract_inputs.py::test_views_are_read_as_raw_bytes[scalar]` |
| M22 | unknown handler not checked | `_codec.py` | `tests/test_contract_inputs.py::test_unknown_codec_and_handler_errors_are_bounded[long]` |
| M23 | exception pickle loses encoding | `_bom.py` | `tests/test_contract_api.py::test_results_and_errors_round_trip_through_pickle[0]` |
| M24 | newline validation removed | `_stream.py` | `tests/test_contract_inputs.py::test_invalid_newlines_fail_before_consuming_input[long]` |

## Final gates

On CPython 3.14.6, each command run separately:

| Command | Result |
| --- | --- |
| ruff format --check . | exit 0, 36 files |
| ruff check . | exit 0 |
| mypy --strict src | exit 0, 11 modules |
| mypy --strict src tests | exit 0, 29 modules |
| pytest | exit 0, 417 passed, 2 platform skips |

The final suite enables fetched sources, Node.js, installed-wheel e2e and the live
PyPI upgrade. Every test has a 300-second timeout. Temporary files and build
environments are confined to the dedicated certification scratch directory.

## Review status

No QA lens or independent reviewer has passed this release yet. Items 16 and 19
remain open. Merge and publication have not been performed.
