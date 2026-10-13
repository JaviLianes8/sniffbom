import dataclasses
import importlib.resources

import pytest

import sniffbom

# The public API. Add every exported name here as the library grows; this list is the
# contract and the test below fails if the module and this list disagree.
PUBLIC_API: list[str] = [
    "ENCODINGS",
    "BomInfo",
    "UnsupportedBomError",
    "WhatwgEncoding",
    "XmlFamily",
    "XmlGuess",
    "bom_sniff",
    "decode",
    "detect",
    "needs_more",
    "strip",
    "text_stream",
    "whatwg_decode",
    "xml_autodetect",
]


def test_all_lists_exactly_the_public_api() -> None:
    assert sorted(sniffbom.__all__) == sorted(PUBLIC_API)


def test_every_exported_name_resolves() -> None:
    for name in sniffbom.__all__:
        assert hasattr(sniffbom, name)


def test_version_is_a_three_part_string() -> None:
    parts = sniffbom.__version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)


def test_the_package_ships_type_information() -> None:
    assert importlib.resources.files("sniffbom").joinpath("py.typed").is_file()


def test_results_are_frozen() -> None:
    for value in (sniffbom.BomInfo("utf-8", 3), sniffbom.xml_autodetect(b"")):
        with pytest.raises(dataclasses.FrozenInstanceError):
            value.codec = "x"  # type: ignore[misc]


def test_the_error_is_a_lookup_error() -> None:
    assert issubclass(sniffbom.UnsupportedBomError, LookupError)
