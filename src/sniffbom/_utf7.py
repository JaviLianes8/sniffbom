"""Remove a UTF-7 mark, whose last byte may share bits with the next character."""

from __future__ import annotations

_BASE64 = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"


def strip_utf7(data: bytes) -> bytes:
    """Return ``data`` (which starts with a UTF-7 mark) without the encoded U+FEFF.

    The mark is the first 16 bits of a modified base64 run (RFC 2152), so the rest of
    the run is re-encoded from bit 16 on. A run whose trailing bits are not zero is
    malformed and cannot be shortened exactly: it is returned unchanged.
    """
    end = 1
    while end < len(data) and data[end] in _BASE64:
        end += 1
    bits = "".join(f"{_BASE64.index(byte):06b}" for byte in data[1:end])
    whole = len(bits) - len(bits) % 16
    if "1" in bits[whole:]:
        return data
    rest = bits[16:whole]
    tail = data[end:]
    if not rest:
        # The run held only the mark: drop it together with its explicit terminator.
        return tail[1:] if tail.startswith(b"-") else tail
    rest += "0" * (-len(rest) % 6)
    run = bytes(_BASE64[int(rest[i : i + 6], 2)] for i in range(0, len(rest), 6))
    return b"+" + run + tail
