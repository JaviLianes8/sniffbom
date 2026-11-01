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
| 10 | PASS | Current wheel: 1170 passed on each of seven distinct builds covering 3.10 to 3.14 and free-threaded 3.14 |
| 11 | PASS | Absolute README links, problem and honest alternatives, guide and changelog, exact certification badge; twine check --strict |
| 12 | PASS | CHANGELOG 1.0.0 dated 2026-11-01 |
| 13 | PASS | Version 1.0.0, Production/Stable, Python 3.10 to 3.14, MIT, project URLs, keywords, no runtime dependencies |
| 14 | PASS | Wheel and sdist lists inspected; LICENSE and py.typed; no fetched content, caches or certification notes in artifacts |
| 15 | PASS | Each gate exits 0 separately; QA lenses round-3 correction suite 1462 passed, 2 platform skips |
| 16 | PENDING | No independent reviewer verdict recorded |
| 17 | PENDING | Release branch prepared; merge and publication remain pending |
| 18 | PASS | 24 initial mutations caught; round-5 survivors, M52/M54, N04/N09 and QA-E-005 through QA-E-008 caught by maintained contracts |
| 19 | PENDING | c PASS remains applicable; latest a/e corrections await independent re-review; b/d need recheck after later runtime changes |

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

The latest QA lenses round 1 reviewed 2c45a87 and reported A-001, QA-E-001 and
QA-E-002. All three are corrected in the final section below and await independent
re-review. Round 4 passed the robustness lens at dd815dd; its runtime source remains
unchanged. Correctness and packaging require recheck after the later codec changes.
Items 16 and 19 remain open. Merge and publication have not been performed.

## QA round 1 corrections

Date: 2026-11-01. Reviewed head: `19552074c06917cd817e9833715fa211a1572bfc`.
Fix commit: `331078331f1bba9297b730c41db459c45267fddc` (`fix qa round one findings`).
All five initial lenses reported FAIL. All 18 findings are addressed below; no
finding is disputed. Independent re-review remains required before certification.

| Finding | Correction and maintained evidence |
| --- | --- |
| A-01 | Surrogate codec names raise bounded LookupError in all three decoders; detected marks override unused names. `test_codec_contracts.py` |
| A-02 | README, GUIDE and WHATWG docstring require replacement compatibility and describe propagated built-in codec exceptions. |
| B-001 | BOCU-1 stripping returns the original bytes, preserving state and both U+FEFF characters. ICU independently encodes and decodes API, file CLI and stdin CLI cases; JSON reports stripped=false. `test_bocu1.py` |
| C-001 | UTF-7 streams reject runs above 65536 base64 bytes with bounded UnicodeError. Tests cover marked/default codecs, later runs, chunk boundaries and finite input consumption. `test_stream_limits.py` |
| C-002 | GB18030 streams reject surrogateescape with bounded LookupError; bulk decoding remains available. EOF repro, empty input, aliases and mark override covered. `test_stream_limits.py` |
| C-003 | Reject undefined, non-strict IDNA and unsupported Punycode policies with bounded LookupError. Compatible policies remain supported; docs describe propagated codec errors. `test_codec_contracts.py` |
| C-004 | Normalize string subclasses and format only canonical names; supplied fields remain available as plain strings. Equality and formatting hooks cannot disclose the canary. `test_codec_contracts.py` |
| C-005 | Validate callable read/close before consumption, including empty among; bounded TypeError. `test_stream_limits.py` |
| C-006, D1 | Escape unrepresentable report characters. Redirected cp1252 inspection, check and multi-file strip run against source and both installed entry points, with marked/unmarked inputs. `test_cli_unicode.py`, `test_e2e_wheel.py` |
| E-01 | Exact bytes type on empty, unmarked and filtered inputs for every supported buffer type. `test_contract_boundaries.py` |
| E-02 | XmlGuess preserves all supplied fields, including negative lengths. `test_contract_boundaries.py` |
| E-03 | Empty among performs zero setup reads, even with a reader that fails if called. `test_contract_boundaries.py` |
| E-04 | Check status remembers a marked file in either file order. `test_contract_boundaries.py` |
| E-05 | Exact diagnostic path boundary at 240/241 characters. `test_contract_boundaries.py` |
| E-06 | Exact 160-character message cap at lengths 160, 161 and 10000. `test_contract_boundaries.py` |
| E-07 | Portable replacement model enforces mode restoration. Real POSIX test remains required through SNIFFBOM_REQUIRE_FILESYSTEM=1. `test_filesystem_contracts.py`, `test_cli.py` |
| E-08 | Portable alias model verifies target update and alias preservation. Real symlink test remains required through SNIFFBOM_REQUIRE_FILESYSTEM=1. `test_filesystem_contracts.py`, `test_review_fixes.py` |

The behavior tests were run before implementation: 70 failures and four passes on
the reviewed source, plus six failures and six passes for the additional Punycode
policy cases before that correction. Every changed behavior is in CHANGELOG.
Existing BOCU-1 byte-slicing expectations were replaced with preservation contracts.
Public names, signatures and defaults remain unchanged.

The eight surviving mutations were each injected into an isolated source copy and
rerun against the new maintained contracts. All eight failed by assertion, with no
collection error or timeout:

| Lens-e mutation | First failing contract |
| --- | --- |
| M22 | test_strip_always_returns_bytes_when_matching_is_disabled |
| M37 | test_xmlguess_preserves_supplied_fields |
| M44 | test_empty_among_never_reads_during_setup |
| M57 | test_check_remembers_any_marked_file |
| M61 | test_diagnostic_path_limit_is_exact, length 241 |
| M62 | test_os_diagnostic_limit_is_exact, length 161 |
| M64 | test_replaceable_read_only_target_restores_mode |
| M65 | test_resolved_alias_keeps_alias_and_updates_target |

The original UTF-7 scaling sizes, 349530 through 5592410 bytes, now reject in median
7.69 to 7.77 ms over five runs each. The largest input no longer requires decoding
its entire shifted run. Maintained tests assert at most 73728 bytes consumed before
failure instead of relying on timing thresholds.

The supported-version suite passes on CPython 3.10.22, 3.11.18, 3.12.16, 3.13.18,
3.14.10 and free-threaded 3.14.10: 530 passed, three skips each. These runs use the
already provisioned local interpreters. Skips are wheel rebuilding (run separately),
POSIX modes and real symlinks. The full 3.14.6 gate includes the wheel built from
sdist, the live 0.2.0 upgrade, both installed CLI entry points, ICU, source references
and Node.js. All tests use a 300-second timeout and dedicated scratch directories.

Portable filesystem models passed and killed M64/M65. Real POSIX permissions and
real symlinks cannot run on this Windows account; WSL is not installed. CONTRIBUTING
requires a POSIX run with SNIFFBOM_REQUIRE_FILESYSTEM=1, which makes either unavailable
check fail rather than skip. No real POSIX or symlink execution is claimed here.

Evidence is retained in the external certification scratch directory
`sniffbom-cert/fix-r1`: red.log, punycode-red.log, mutation-results.json, M22/M37/M44/
M57/M61/M62/M64/M65.log, scaling-results.json and matrix-results.json.

Final round-1 gates, each executed separately on CPython 3.14.6:

| Command | Result |
| --- | --- |
| ruff format --check . | exit 0, 42 files |
| ruff check . | exit 0 |
| mypy --strict src | exit 0, 11 modules |
| mypy --strict src tests | exit 0, 35 modules |
| pytest --timeout=300 | exit 0, 531 passed, two platform skips, 20.00 seconds |

All eleven reference files were fetched again and verified against the manifest
before this final suite. Its output is retained in `fix-r1/final.log`.

## QA round 2 corrections

Date: 2026-11-01. Reviewed head: `1802b7f338891108986055bc79d0e3ab588e84ac`.
Fix commit: `d32cd99939f874c9e37d8cdc6ebeec4c57e81a5e` (`fix qa round two findings`).
All six reported findings are addressed; none is disputed. The round-3 rechecks
independently confirmed these fixes and reported the additional findings below.

The five round-2 reports, retained under the external certification scratch
directory as `lens-<letter>-r2/REPORT.md`, record these results for the reviewed head:

| Lens | Verdict | Findings |
| --- | --- | --- |
| a: API and docs | PASS | None |
| b: Correctness and ground truth | PASS | None |
| c: Adversarial and robustness | FAIL | C-007 |
| d: Packaging and real e2e | PASS | None |
| e: Contract strength | FAIL | E-09 through E-13 |

| Finding | Correction and maintained evidence |
| --- | --- |
| C-007 | Normalize selected codec and error-policy strings with `str.__str__` before validation, retain those values through decoding and the GB18030 guard. Equality, iteration, containment and string-conversion overrides cannot bypass validation. Bounded errors, supported policies and BOM precedence are covered in `test_codec_subclasses.py`; GUIDE and CHANGELOG describe the behavior. |
| E-09 | Missing and non-callable `read` with callable `close` must raise bounded TypeError at setup, both with normal sniffing and empty `among`. `test_stream_limits.py` |
| E-10 | Exactly 65537 base64 bytes must raise the UTF-7 guard error with strict, replace and ignore policies across two chunk sizes; existing 65536-byte acceptance remains covered. `test_stream_limits.py` |
| E-11 | A valid shifted run containing 65544 interior plus bytes must hit the guard across reader chunks. Python bulk decoding independently accepts the input. `test_stream_limits.py` |
| E-12 | Long plus-prefixed ASCII must decode completely through UTF-8 and Latin-1, with EOF on the next read. `test_stream_limits.py` |
| E-13 | The public module CLI runs with explicitly configured cp1252/strict stderr: a missing Unicode path yields status 2, an escaped diagnostic, no traceback and a report for the later valid path. `test_cli_unicode.py` |

The behavior contracts were added and executed before changing runtime code: 20
failures and 61 passes across the three affected test modules. The failures include
all four subclass bypasses from C-007, plus hidden NULs and incorrectly rejected
supported policies. After the correction, the focused decoder, stream and CLI
contracts passed all 202 cases. Public names, signatures and defaults are unchanged.

E-09 through E-13 required regression tests; the existing implementation already
satisfied their witnesses. Each exact reported mutation was injected separately
into a scratch source copy and tested against the new maintained contracts. The 23
targeted cases passed before mutation and after byte-for-byte restoration. All five
mutations failed their contracts, with no collection error or timeout:

| Lens-e mutation | Failing contract |
| --- | --- |
| N15 | test_closeable_reader_still_requires_callable_read |
| N22 | test_first_byte_over_utf7_limit_is_rejected |
| N26 | test_plus_counts_inside_utf7_shifted_run |
| N28 | test_long_ascii_run_remains_valid_in_non_utf7_stream |
| N31 | test_unicode_error_report_preserves_status_and_later_paths |

Round-2 gates, each executed separately on CPython 3.14.6:

| Command | Result |
| --- | --- |
| ruff format --check . | exit 0, 43 files |
| ruff check . | exit 0 |
| mypy --strict src | exit 0, 11 modules |
| mypy --strict src tests | exit 0, 36 modules |
| pytest --timeout=300 | exit 0, 577 passed, two platform skips |

All eleven reference files were fetched again and verified against the manifest.
The full suite enables ICU, Node.js, wheel-from-sdist installation, both installed
CLI entry points and the live 0.2.0 upgrade. The two existing skips are POSIX file
modes and real symlink creation on Windows; their portable models pass. No new
interpreter matrix is claimed for this bounded correction. Tests have a 300-second
timeout; all temporary files and caches stay under certification scratch.

Evidence is retained in `sniffbom-cert/fix-r2`: `red.log`, `green.log`,
`mutation-results.json`, `baseline.log`, `N15.log`, `N22.log`, `N26.log`, `N28.log`,
`N31.log`, `restored.log`, `fetch.log`, `full.log` and the final gate logs.

## QA round 3 corrections

Date: 2026-11-01. Reviewed head: `6d5ce1f8792261dc352e87c1515b8d87ee126c11`.
Fix commit: `82a4056afb9ca539e7c0d0ac028089befe08dc24` (`fix qa round three findings`).
All eight reported findings are addressed; none is disputed. The round-4 rechecks
independently confirmed these fixes and reported the additional findings below.

The two round-3 reports, retained under the external certification scratch
directory as `lens-<letter>-r3/REPORT.md`, record these results for the reviewed head:

| Lens | Verdict | Findings |
| --- | --- | --- |
| c: Adversarial and robustness | FAIL | C-007 fixed; new C-008 |
| e: Contract strength | FAIL | E-09 through E-13 fixed; new E-14 through E-20 |

| Finding | Correction and maintained evidence |
| --- | --- |
| C-008 | Reject surrogates in the normalized error-policy name before registry lookup with bounded LookupError. Empty, valid and marked input, plain strings, subclasses and all surrogate-range endpoints are covered; exception type, arguments, representation and chaining are pinned in `test_error_policy_contracts.py`. GUIDE and CHANGELOG record the behavior. |
| E-14 | Registered mixed-case names execute their exact handler through bulk and streaming decoding, with marked/unmarked input and plain/subclass policy names. `test_registered_error_handler_names_are_exact` |
| E-15 | Registered names with surrounding spaces retain significant whitespace and execute their exact handler through both decoders. `test_registered_error_handler_names_are_exact` |
| E-16 | Non-ASCII unmarked bulk input uses the underlying Latin-1 fallback even when its string subclass returns UTF-8 from `__str__`. `test_decoding_keeps_the_underlying_fallback[bulk]` |
| E-17 | Malformed marked bulk input uses the underlying ignore policy even when its string subclass returns strict from `__str__`. `test_decoding_keeps_the_underlying_error_policy[marked-bulk]` |
| E-18 | Non-ASCII stream input uses the underlying Latin-1 fallback despite its string-conversion override. `test_decoding_keeps_the_underlying_fallback[stream]` |
| E-19 | Malformed marked and unmarked streams retain the underlying ignore policy, return the expected text and reach EOF. `test_decoding_keeps_the_underlying_error_policy` |
| E-20 | Malformed unmarked bulk input retains the underlying ignore policy. `test_decoding_keeps_the_underlying_error_policy[unmarked-bulk]` |

The contracts were added and executed before changing runtime code: 64 failures
and 45 passes. Every failure was the reported UnicodeEncodeError from looking up a
surrogate-containing policy. After the correction, all 152 focused codec and policy
cases passed. The exact original P22 input also raises the required bounded
LookupError. Public names, signatures and defaults remain unchanged.

E-14 through E-20 were missing contracts for behavior the implementation already
provided. Each exact reported mutation was injected separately into a scratch
source copy. All seven failed the maintained contracts, with no collection errors
or timeouts. The 22 targeted cases passed before mutation and after byte-for-byte
source restoration:

| Lens-e mutation | Failing contract |
| --- | --- |
| R07 | test_registered_error_handler_names_are_exact, mixed-case names |
| R08 | test_registered_error_handler_names_are_exact, surrounding spaces |
| R12 | test_decoding_keeps_the_underlying_fallback, bulk |
| R14 | test_decoding_keeps_the_underlying_error_policy, marked bulk |
| R15 | test_decoding_keeps_the_underlying_fallback, stream |
| R16 | test_decoding_keeps_the_underlying_error_policy, marked and unmarked streams |
| R18 | test_decoding_keeps_the_underlying_error_policy, unmarked bulk |

Round-3 gates, each executed separately on CPython 3.14.6:

| Command | Result |
| --- | --- |
| ruff format --check . | exit 0, 44 files |
| ruff check . | exit 0 |
| mypy --strict src | exit 0, 11 modules |
| mypy --strict src tests | exit 0, 37 modules |
| pytest --timeout=300 | exit 0, 663 passed, two platform skips |

All eleven reference files were fetched again and verified against the manifest.
The full suite enables ICU, Node.js, wheel-from-sdist installation, both installed
CLI entry points and the live 0.2.0 upgrade. The existing Windows skips are POSIX
file modes and real symlink creation; their portable contracts pass. No new
interpreter matrix is claimed for this bounded correction. Every test has a
300-second timeout; temporary files and caches stay under certification scratch.

Evidence is retained in `sniffbom-cert/fix-r3`: `red.log`, `green.log`, `c008.log`,
`mutation-results.json`, `baseline.log`, `R07.log`, `R08.log`, `R12.log`, `R14.log`,
`R15.log`, `R16.log`, `R18.log`, `restored.log`, their JUnit XML reports, `fetch.log`,
`final.log` and the final gate logs.

## QA round 4 corrections

Date: 2026-11-01. Reviewed head: `dd815dd47da601d6f7101d4612ebb55a0233bbd8`.
Fix commit: `4a78973307ea11c7425b713a2729c5fe892fc827` (`fix qa round four findings`).
All three reported findings are addressed; none is disputed. The round-5 recheck
independently confirmed these fixes and reported the additional findings below.

The round-4 reports are retained under the external certification scratch directory
as `lens-<letter>-r4/REPORT.md`:

| Lens | Verdict | Findings |
| --- | --- | --- |
| c: Adversarial and robustness | PASS | C-008 fixed; no new findings |
| e: Contract strength | FAIL | E-14 through E-20 fixed; new E-21 through E-23 |

| Finding | Correction and maintained evidence |
| --- | --- |
| E-21 | Registered names containing U+D7FF invoke the handler and match Python's UTF-8 decoder through bulk and streaming decoding, marked/unmarked input and plain/subclass names. `test_registered_error_handler_names_are_exact` |
| E-22 | The same contract accepts registered names containing U+E000, pinning both valid boundaries adjacent to the surrogate interval. `test_registered_error_handler_names_are_exact` |
| E-23 | Leading, interior and trailing surrogates at all four surrogate-range endpoints raise exact bounded LookupError, without retained input or exception chaining. Covers empty, valid and malformed payloads, marked/unmarked input, plain/subclass policy names and both decoders. `test_surrogate_error_policies_raise_bounded_lookup_errors` |

These were missing regression contracts for behavior the implementation already
provided. Runtime code and the public API remain unchanged. CHANGELOG records the
new coverage. All 324 policy contract cases pass on the reviewed runtime source.

Each exact S07, S08 and S10 replacement from the reviewer's frozen mutation file was
applied alone in a scratch source copy. Before the test changes, all three survived
the 84 existing policy cases. After the changes, all three failed genuine contract
assertions or expected exception checks, with no collection errors or timeouts:

| Lens-e mutation | Failing contract | Failures |
| --- | --- | ---: |
| S07: reject U+D7FF | test_registered_error_handler_names_are_exact, U+D7FF names | 8 |
| S08: reject U+E000 | test_registered_error_handler_names_are_exact, U+E000 names | 8 |
| S10: scan only the final character | test_surrogate_error_policies_raise_bounded_lookup_errors, leading and interior positions | 192 |

The clean baseline and byte-for-byte restored source each pass all 324 cases.
Mutation runs disable bytecode caching and enforce a 300-second per-test timeout.

Round-4 gates, each executed separately on CPython 3.14.6:

| Command | Result |
| --- | --- |
| ruff format --check . | exit 0, 44 files |
| ruff check . | exit 0 |
| mypy --strict src | exit 0, 11 modules |
| mypy --strict src tests | exit 0, 37 modules |
| pytest --timeout=300 | exit 0, 903 passed, two platform skips |

All eleven reference files were fetched again and verified against the manifest.
The full suite enables ICU, Node.js, wheel-from-sdist installation, both installed
CLI entry points and the live 0.2.0 upgrade. The existing Windows skips are POSIX
file modes and real symlink creation; their portable contracts pass. No new
interpreter matrix is claimed for this bounded correction. Every test has a
300-second timeout; temporary files and caches stay under certification scratch.

Evidence is retained in `sniffbom-cert/fix-r4`: `before-mutation-results.json`,
`after-mutation-results.json`, the `before-*` and `after-*` logs and JUnit reports,
`fetch.log`, `final-gates.json`, `final-*.log` and `final.xml`. The gates also pass
after recording the fix commit; that run is retained as `report-gates.json`,
`report-*.log` and `report.xml`.

## QA round 5 corrections

Date: 2026-11-01. Reviewed head: `c86c369eed0a222861013b4584c4531685f31f31`.
Fix commit: `c7af6dfd15fcc11d6395937fb3c5833ace6bf111` (`fix qa round five findings`).
Both reported findings are addressed; neither is disputed. Independent re-review
of these corrections remains required.

The round-5 report is retained under the external certification scratch directory
as `lens-e-r5/REPORT.md`:

| Lens | Verdict | Findings |
| --- | --- | --- |
| e: Contract strength | FAIL | E-21 through E-23 fixed; new E-24 and E-25 |

| Finding | Correction and maintained evidence |
| --- | --- |
| E-24 | Distinct composed and decomposed names register different handlers. Both names select their exact callback, matching Python's native UTF-8 decoder through bulk and streaming decoding, marked/unmarked input and plain/subclass policy names. `test_registered_handler_names_preserve_unicode_form` |
| E-25 | Adjacent high/low surrogate pairs at both range endpoints raise exact bounded LookupError in codec and policy names, without retained input or exception chaining. Covers leading/interior/trailing pairs, long names, empty/valid/malformed input and string subclasses. Both decoders reject marked and unmarked policies; all three decoders reject unmarked fallbacks and preserve mark precedence. `test_surrogate_error_policies_raise_bounded_lookup_errors`, `test_paired_surrogate_codec_names_raise_bounded_lookup_errors` |

These were missing regression contracts for behavior the reviewed implementation
already provided. Runtime code and the public API remain unchanged. CHANGELOG
records the added coverage. All 635 focused codec and policy cases pass on the
reviewed runtime source.

Each exact T04 and T10 replacement from the reviewer's frozen mutation manifest was
applied alone in a scratch source copy, with its baseline hash checked. Before the
test changes, both survived all 367 existing focused cases. After the changes,
both failed genuine assertions or expected exception checks, without collection
errors or timeouts:

| Lens-e mutation | Failing contract | Failures |
| --- | --- | ---: |
| T04: NFC-normalize registered policy names | test_registered_handler_names_preserve_unicode_form, decomposed names | 8 |
| T10: reject only unpaired surrogates | test_surrogate_error_policies_raise_bounded_lookup_errors, paired units; test_paired_surrogate_codec_names_raise_bounded_lookup_errors | 252 |

The clean baseline and byte-for-byte restored source each pass all 635 cases.
Mutation runs disable bytecode caching and enforce a 300-second per-test timeout.

Round-5 gates, each executed separately on CPython 3.14.6:

| Command | Result |
| --- | --- |
| ruff format --check . | exit 0, 44 files |
| ruff check . | exit 0 |
| mypy --strict src | exit 0, 11 modules |
| mypy --strict src tests | exit 0, 37 modules |
| pytest --timeout=300 | exit 0, 1171 passed, two platform skips |

All eleven reference files were fetched again and verified against the manifest.
The full suite enables ICU, Node.js, wheel-from-sdist installation, both installed
CLI entry points and the live 0.2.0 upgrade. The existing Windows skips are POSIX
file modes and real symlink creation; their portable contracts pass. No new
interpreter matrix is claimed for this bounded correction. Every test has a
300-second timeout; temporary files and caches stay under certification scratch.

Evidence is retained in `sniffbom-cert/fix-r5`: `before-mutation-results.json`,
`after-mutation-results.json`, the `before-*` and `after-*` logs and JUnit reports,
`fetch.log`, `final-gates.json`, `final-*.log` and `final.xml`. The gates also pass
after recording the fix commit; that run is retained as `report-gates.json`,
`report-*.log` and `report.xml`.

## Resumed preparation verification

Date: 2026-11-01. Starting head: `b017c77f6fc55bfa4c78c845b1138d057a44c2c1`.
The release branch was clean and already pushed. Earlier completed work and all
mutation evidence are retained. This preparation update changes only this report.

The interpreter matrix was refreshed because its earlier runs preceded the final
codec correction. The round-5 wheel and sdist match every current packaged file
byte for byte. Their file lists were inspected again and both pass
`twine check --strict`. PyPI's JSON endpoint still reports 0.2.0. All eleven
reference files were fetched live again and match the tracked manifest hashes.

Each interpreter received a fresh venv with the current wheel. The suite ran from
the extracted sdist with its source directory moved out of the import path and
`python -I`; imports resolve to site-packages. Both installed CLI entry points
passed separate subprocess checks. ICU, Node.js and fetched-source checks ran.

| Interpreter | Current wheel suite |
| --- | --- |
| CPython 3.10.22 | 1170 passed, 3 skipped |
| CPython 3.11.18 | 1170 passed, 3 skipped |
| CPython 3.12.16 | 1170 passed, 3 skipped |
| CPython 3.13.18 | 1170 passed, 3 skipped |
| CPython 3.14.6 | 1170 passed, 3 skipped |
| CPython 3.14.10 | 1170 passed, 3 skipped |
| CPython 3.14.10t | 1170 passed, 3 skipped |

The matrix skips rebuilding the wheel, which runs in the full gate below, and the
same two unavailable Windows filesystem checks. Launcher entries still point to
thirteen removed installations; scratch interpreter aliases resolve to the seven
distinct builds above. No supported minor version is untested.

Final gates each exit 0: `ruff format --check .` (44 files), `ruff check .`,
`mypy --strict src` (11 modules), `mypy --strict src tests` (37 modules) and
`pytest --timeout=300` (1171 passed, two platform skips). This full run includes
the wheel built from sdist, fresh installation, both CLI entry points and upgrade
from the actual PyPI 0.2.0 release. All temporary files and caches remain under
the certification scratch directory.

Evidence is retained in `sniffbom-cert/preparation-resume`: `verify.py`,
`matrix.json`, `pytest-*.log`, `artifacts.json`, both archive listings, `twine.log`,
`pypi.json`, `fetch.log`, `final-gates.json`, `final-*.log` and `final.xml`.
Only lens c's existing PASS remains applicable to the unchanged runtime source.
Lenses a, b and d require recheck after the later codec changes; lens e's latest
corrections and the independent reviewer remain pending. PR #3 remains open;
merge and publication have not been performed.

## QA lenses round 1 corrections

Date: 2026-11-01. Reviewed head: `2c45a877922e1ec3173b1f893ed4bb006af23b63`.
Fix commit: `7e2638a4d36fbdef19b51fbc1fc4cd0b1208b6e0` (`fix qa lens round one findings`).
All three findings are addressed; none is disputed. The latest reports are retained
under certification scratch as `lens-a-r1/REPORT.md` and `lens-e-r1/REPORT.md`.
Independent re-review remains required; this correction does not record new lens verdicts.

| Finding | Correction and evidence |
| --- | --- |
| A-001 | README lists `errors="strict"`, `among=None` and `newline=None` for `text_stream`. All eight documented function signatures match runtime parameter names, kinds and defaults. |
| QA-E-001 | `test_bom_sniff_ignores_nonleading_marks` asserts `None` for nonleading UTF-8, UTF-16LE and UTF-16BE marks at offsets 1, 2 and 4 across bytes, bytearray and memoryview. |
| QA-E-002 | `test_xml_autodetect_ignores_nonleading_marks` asserts the complete `XmlGuess("other", 0, "utf-8")` for the same marks, offsets and buffer types. |

The two contract findings concern missing tests for behavior already provided by
the reviewed implementation. All 54 new cases pass on the unchanged runtime source.
Runtime behavior, public names, signatures and defaults remain stable. CHANGELOG
records the added coverage and corrected documentation.

Each reported mutation replaced `if head.startswith(mark):` with `if mark in head:`
alone in a scratch source copy. Each test process disabled bytecode writes and used
a 300-second per-test timeout. Both mutations fail actual assertions:

| Mutation | Catching contract | Result |
| --- | --- | --- |
| M52 in `_whatwg.py` | `test_bom_sniff_ignores_nonleading_marks` | 6 failures, 48 passes |
| M54 in `_xml.py` | `test_xml_autodetect_ignores_nonleading_marks` | 15 failures, 39 passes |

The baseline and byte-for-byte restored source each pass all 54 cases. No runtime
file in the release checkout was mutated.

Final gates on CPython 3.14.6, each executed separately:

| Command | Result |
| --- | --- |
| ruff format --check . | exit 0, 44 files |
| ruff check . | exit 0 |
| mypy --strict src | exit 0, 11 modules |
| mypy --strict src tests | exit 0, 37 modules |
| pytest --timeout=300 | exit 0, 1225 passed, two platform skips |

The suite includes the hash-verified reference files retained from preparation,
ICU and Node.js comparisons, wheel-from-sdist installation, both installed CLI
entry points and upgrade from PyPI 0.2.0. The skips remain POSIX file modes and
real symlink creation on this Windows account. Scratch files, caches and pytest
basetemps stay under `sniffbom-cert/fix-qa-lenses-r1`.

Evidence there includes `mutation-results.json`, `baseline.log`, `M52.log`,
`M54.log`, `restored.log`, their JUnit reports, `source-hashes.json`,
`readme-signatures.log`, `final-gates.json`, `final-*.log` and `final.xml`.

## QA lenses round 2 corrections

Date: 2026-11-01. Reviewed head: `a3239aef25df43b43f360c6a21138d59d057d870`.
Fix commit: `597189cf2993a182fbf3a57b199ec50eaf700328` (`fix qa lens round two findings`).
Both findings are addressed; neither is disputed. The review report is retained
under certification scratch as `lens-e-r2/REPORT.md`. Independent re-review
remains required; this correction does not record a new lens verdict.

| Finding | Correction and evidence |
| --- | --- |
| QA-E-003 | `test_bom_sniff_rejects_nul_prefixed_utf16_marks` asserts `None` for both UTF-16 marks preceded by one NUL byte across bytes, bytearray and memoryview: six cases. |
| QA-E-004 | `test_xml_autodetect_requires_complete_unmarked_signatures` asserts the complete `XmlGuess("other", 0, "utf-8")` for lengths one, two and three of all eight unmarked signatures across bytes, bytearray and memoryview: 72 cases. |

These findings concern missing contracts for behavior the reviewed implementation
already provides. All 78 new cases pass on the unchanged runtime source. Public
names, signatures, defaults and runtime behavior remain stable. CHANGELOG records
the additional coverage.

Each exact reported mutation was applied alone in a scratch source copy. Both
survived all 89 existing WHATWG/XML cases before the new contracts. Afterward,
each fails actual assertions, without collection errors or timeouts:

| Mutation | Catching contract | Result |
| --- | --- | --- |
| N04: strip leading NUL bytes from the BOM sniffing head | test_bom_sniff_rejects_nul_prefixed_utf16_marks | 6 failures, 161 passes |
| N09: accept nonempty proper prefixes of unmarked XML signatures | test_xml_autodetect_requires_complete_unmarked_signatures | 72 failures, 95 passes |

The baseline and byte-for-byte restored source each pass all 167 focused cases.
Mutation processes disable bytecode writes and use a 300-second per-test timeout.
No runtime file in the release checkout was mutated.

Final gates on CPython 3.14.6, each executed separately:

| Command | Result |
| --- | --- |
| ruff format --check . | exit 0, 44 files |
| ruff check . | exit 0 |
| mypy --strict src | exit 0, 11 modules |
| mypy --strict src tests | exit 0, 37 modules |
| pytest --timeout=300 | exit 0, 1303 passed, two platform skips |

The full suite includes the hash-verified reference files retained from preparation,
ICU and Node.js comparisons, wheel-from-sdist installation, both installed CLI
entry points and upgrade from PyPI 0.2.0. The skips remain POSIX file modes and
real symlink creation on this Windows account. No new interpreter matrix is claimed
for this bounded correction. Scratch files, caches and pytest basetemps stay under
`sniffbom-cert/fix-qa-lenses-r2`.

Evidence there includes `verify.py`, `before-mutation-results.json`,
`after-mutation-results.json`, the `before-*` and `after-*` logs, JUnit reports and
source hashes, plus `final-gates.json`, `final-*.log` and `final.xml`. The final
report check is retained as `report-gates.json`, `report-*.log` and `report.xml`.

## QA lenses round 3 corrections

Date: 2026-11-01. Reviewed head: `b002d1504401ca91b70dec3b7825c2db46b4b6b6`.
Fix commit: `8774d37cde7f5580dd8ca2745efdab9440a2f6aa` (`fix qa lens round three findings`).
All four findings are addressed; none is disputed. The review report is retained
under certification scratch as `lens-e-r3/REPORT.md`. Independent re-review
remains required; this correction does not record a new lens verdict.

The hand-derived contracts in `tests/test_sniff_contracts.py` cover bytes,
bytearray and memoryview inputs and assert every XML result field:

| Finding | Correction |
| --- | --- |
| QA-E-005 | Both complete two-byte UTF-16 marks are recognized without payload: six cases. |
| QA-E-006 | Single-byte FE, FF and EF prefixes return None: nine cases. |
| QA-E-007 | All seven XML marks preceded by each of the six ASCII whitespace bytes return XmlGuess("other", 0, "utf-8"): 126 cases. |
| QA-E-008 | Three case variants of the ASCII signature and three ASCII byte-case variants of the EBCDIC signature return XmlGuess("other", 0, "utf-8"): 18 cases. |

These are missing-contract findings for behavior the reviewed implementation
already provides. All 159 added cases pass on the unchanged runtime source.
Public names, signatures, defaults and runtime behavior remain stable. CHANGELOG
records the added coverage.

Each exact reported mutation was applied alone in a scratch source copy. All four
survived the 167 existing WHATWG/XML cases before the new contracts. Afterward,
each fails actual assertions, without collection errors or timeouts:

| Mutation | Catching contract | Result |
| --- | --- | --- |
| QA-E-005: require a three-byte head for UTF-16 marks | test_bom_sniff_accepts_complete_utf16_marks_without_payload | 6 failures, 320 passes |
| QA-E-006: pad the head with FF bytes | test_bom_sniff_rejects_single_byte_prefixes | 3 failures, 323 passes |
| QA-E-007: strip leading ASCII whitespace from the XML head | test_xml_autodetect_rejects_whitespace_prefixed_marks | 90 failures, 236 passes |
| QA-E-008: fold byte case when matching XML signatures | test_xml_autodetect_requires_literal_signature_case | 18 failures, 308 passes |

The baseline and byte-for-byte restored source each pass all 326 focused cases.
Mutation processes disable bytecode writes and use a 300-second per-test timeout.
No runtime file in the release checkout was mutated.

Final gates on CPython 3.14.6, each executed separately:

| Command | Result |
| --- | --- |
| ruff format --check . | exit 0, 45 files |
| ruff check . | exit 0 |
| mypy --strict src | exit 0, 11 modules |
| mypy --strict src tests | exit 0, 38 modules |
| pytest --timeout=300 | exit 0, 1462 passed, two platform skips |

The full suite includes the hash-verified reference files retained from preparation,
ICU and Node.js comparisons, wheel-from-sdist installation, both installed CLI
entry points and upgrade from PyPI 0.2.0. The skips remain POSIX file modes and
real symlink creation on this Windows account. No new interpreter matrix is claimed
for this bounded correction. Scratch files, caches and pytest basetemps stay under
`sniffbom-cert/fix-qa-lenses-r3`.

Evidence there includes `verify.py`, `before-mutation-results.json`,
`after-mutation-results.json`, the `before-*` and `after-*` logs, JUnit reports and
source hashes, plus `final-gates.json`, `final-*.log` and `final.xml`. The final
report check is retained as `report-gates.json`, `report-*.log` and `report.xml`.
