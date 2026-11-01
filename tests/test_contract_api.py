"""Stable public names, signatures, result semantics and serialisation."""

from __future__ import annotations

import copy
import dataclasses
import inspect
import pickle
from typing import get_args, get_type_hints

import pytest

import sniffbom
from sniffbom import BomInfo, UnsupportedBomError, XmlGuess


def test_no_accidental_public_attributes() -> None:
    assert {name for name in vars(sniffbom) if not name.startswith("_")} == set(sniffbom.__all__)
    assert len(sniffbom.__all__) == len(set(sniffbom.__all__)) == 14


@pytest.mark.parametrize(
    ("name", "parameters", "defaults"),
    [
        ("detect", ("data", "among"), {"among": None}),
        ("strip", ("data", "among"), {"among": None}),
        ("needs_more", ("data", "among"), {"among": None}),
        (
            "decode",
            ("data", "default", "errors", "among"),
            {"default": "utf-8", "errors": "strict", "among": None},
        ),
        (
            "text_stream",
            ("binary", "default", "errors", "among", "newline"),
            {"default": "utf-8", "errors": "strict", "among": None, "newline": None},
        ),
        ("bom_sniff", ("data",), {}),
        ("whatwg_decode", ("data", "fallback"), {"fallback": "utf-8"}),
        ("xml_autodetect", ("data",), {}),
        ("BomInfo", ("encoding", "length"), {}),
        ("XmlGuess", ("family", "bom_length", "codec"), {}),
        ("UnsupportedBomError", ("encoding",), {}),
    ],
)
def test_parameter_names_defaults_and_kinds_are_stable(
    name: str, parameters: tuple[str, ...], defaults: dict[str, object]
) -> None:
    signature = inspect.signature(getattr(sniffbom, name))
    assert tuple(signature.parameters) == parameters
    for param in signature.parameters.values():
        assert param.default == defaults.get(param.name, inspect.Parameter.empty)
        keyword = param.name in {"among", "errors", "newline"}
        expected = (
            inspect.Parameter.KEYWORD_ONLY if keyword else inspect.Parameter.POSITIONAL_OR_KEYWORD
        )
        assert param.kind == expected


def test_public_annotations_resolve_without_any() -> None:
    for name in sniffbom.__all__:
        obj = getattr(sniffbom, name)
        if inspect.isfunction(obj) or inspect.isclass(obj):
            hints = get_type_hints(obj)
            if inspect.isfunction(obj):
                assert "return" in hints
            assert "typing.Any" not in repr(hints)


def test_literal_aliases_and_encoding_order_are_exact() -> None:
    assert get_args(sniffbom.WhatwgEncoding) == ("UTF-8", "UTF-16BE", "UTF-16LE")
    assert get_args(sniffbom.XmlFamily) == (
        "ucs-4-1234",
        "ucs-4-4321",
        "ucs-4-2143",
        "ucs-4-3412",
        "utf-16-be",
        "utf-16-le",
        "utf-8",
        "ascii",
        "ebcdic",
        "other",
    )
    assert sniffbom.ENCODINGS == (
        "utf-32-le",
        "utf-32-be",
        "gb18030",
        "utf-ebcdic",
        "utf-7",
        "utf-8",
        "utf-1",
        "scsu",
        "bocu-1",
        "utf-16-le",
        "utf-16-be",
    )


def test_records_keep_field_order_equality_hash_and_replace() -> None:
    for record in (BomInfo("utf-8", 3), XmlGuess("utf-8", 3, "utf-8")):
        assert dataclasses.replace(record) == record
        assert hash(dataclasses.replace(record)) == hash(record)
        assert copy.copy(record) == copy.deepcopy(record) == record
        assert record.__class__.__module__ == "sniffbom"
    assert dataclasses.astuple(BomInfo("unknown", -1)) == ("unknown", -1)
    assert BomInfo("unknown", -1).codec is None
    assert BomInfo("utf-8", 3) != BomInfo("utf-8", 2)
    assert repr(BomInfo("utf-8", 3)) == "BomInfo(encoding='utf-8', length=3)"


@pytest.mark.parametrize("protocol", range(pickle.HIGHEST_PROTOCOL + 1))
def test_results_and_errors_round_trip_through_pickle(protocol: int) -> None:
    for record in (BomInfo("utf-8", 3), XmlGuess("utf-8", 3, "utf-8")):
        assert pickle.loads(pickle.dumps(record, protocol)) == record
    error = UnsupportedBomError("scsu")
    for clone in (
        copy.copy(error),
        copy.deepcopy(error),
        pickle.loads(pickle.dumps(error, protocol)),
    ):
        assert type(clone) is UnsupportedBomError
        assert clone.encoding == "scsu" and clone.args == error.args
