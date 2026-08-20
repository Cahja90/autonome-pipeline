"""kleine pngs fuer tests."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

import config


def png_bytes(
    breite: int,
    hoehe: int,
    rgb: tuple[int, int, int],
    extra: int = 0,
) -> bytes:
    r, g, b = rgb

    def chunk(typ: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(typ + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + typ + data + struct.pack(">I", crc)

    roh = b"".join(b"\x00" + bytes([r, g, b]) * breite for _ in range(hoehe))
    body = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", breite, hoehe, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(roh, 9))
        + chunk(b"IEND", b"")
    )
    if extra > 0:
        body += b"\x00" * extra
    return body


def pad_png(pfad: Path, rgb: tuple[int, int, int], px: int = 8) -> None:
    roh = png_bytes(px, px, rgb)
    extra = max(0, config.MIN_FRAME_BYTES - len(roh))
    pfad.write_bytes(png_bytes(px, px, rgb, extra))
