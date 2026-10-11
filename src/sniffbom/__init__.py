"""Detect, name and strip the Unicode byte-order mark on a byte string."""

from __future__ import annotations

from ._bom import BomInfo, decode, detect, strip

__version__ = "0.1.0"

__all__ = ["BomInfo", "decode", "detect", "strip"]
