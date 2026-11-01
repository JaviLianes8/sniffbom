"""Execute API docstrings, including constant attribute docs, and guide examples."""

from __future__ import annotations

import ast
import contextlib
import doctest
import importlib
import io
import re
from pathlib import Path

import sniffbom

ROOT = Path(__file__).resolve().parents[1]


def test_all_public_docstrings_have_executable_examples() -> None:
    names = set(sniffbom.__all__) - {"ENCODINGS", "WhatwgEncoding", "XmlFamily"}
    for name in names:
        assert ">>>" in (getattr(sniffbom, name).__doc__ or ""), name
    assert ">>>" in (sniffbom.BomInfo.codec.__doc__ or "")


def test_docstrings_run_including_attribute_and_property_examples() -> None:
    parser = doctest.DocTestParser()
    runner = doctest.DocTestRunner()
    count = 0
    for path in Path(sniffbom.__file__).parent.glob("*.py"):
        module = importlib.import_module(f"sniffbom.{path.stem}")
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                text = node.value.value
                if isinstance(text, str) and ">>>" in text:
                    test = parser.get_doctest(text, vars(module).copy(), path.stem, str(path), 0)
                    runner.run(test)
                    count += 1
    result = runner.summarize()
    assert count == 15
    assert result.failed == 0 and result.attempted >= 30


def test_guide_examples_print_the_documented_output() -> None:
    text = (ROOT / "GUIDE.md").read_text(encoding="utf-8")
    fence = chr(96) * 3
    blocks = re.findall(fence + r"python\n(.*?)" + fence, text, re.S)
    assert len(blocks) == 2
    for block in blocks:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(compile(block, "GUIDE.md", "exec"), {})
        expected = [line[2:] for line in block.splitlines() if line.startswith("# ")]
        assert output.getvalue().splitlines() == expected


def test_readme_links_are_absolute_and_required_docs_are_linked() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    links = re.findall(r"\]\(([^)]+)\)", text)
    assert all(link.startswith("https://") for link in links)
    assert any(link.endswith("/GUIDE.md") for link in links)
    assert any(link.endswith("/CHANGELOG.md") for link in links)
    badge = (
        "[![Lianes8 Certified](https://lianes8studio.com/certified/"
        "lianes8-certified-badge.svg)](https://lianes8studio.com/certified)"
    )
    assert badge in text
