"""gemalte ansicht. kein foto, kein text, kein name."""

from __future__ import annotations

import struct
import zlib


BREITE = 480
HOEHE = 270


def szene_png(
    breite: int = BREITE,
    hoehe: int = HOEHE,
    saat: int = 1,
    nah: bool = False,
) -> bytes:
    #himmel, boden, block, oeffnung
    roh = bytearray()
    for y in range(hoehe):
        roh.append(0)
        for x in range(breite):
            r, g, b = _farbe(x, y, breite, hoehe, saat, nah)
            roh.extend((r, g, b))
    return _png(breite, hoehe, bytes(roh))


def _farbe(
    x: int,
    y: int,
    breite: int,
    hoehe: int,
    saat: int,
    nah: bool,
) -> tuple[int, int, int]:
    horizont = int(hoehe * (0.58 if nah else 0.64))
    block_links = int(breite * (0.22 if nah else 0.30))
    block_rechts = int(breite * (0.78 if nah else 0.70))
    block_oben = int(hoehe * (0.22 if nah else 0.34))
    loch_links = int(breite * (0.42 if nah else 0.46))
    loch_rechts = int(breite * (0.58 if nah else 0.54))
    loch_oben = int(hoehe * (0.34 if nah else 0.46))
    if block_links <= x < block_rechts and block_oben <= y < horizont:
        if loch_links <= x < loch_rechts and loch_oben <= y < horizont:
            return (32, 28, 26)
        return _klamm(128 + saat * 3), _klamm(112), _klamm(98)
    if y < horizont:
        anteil = y / max(horizont, 1)
        return (
            _klamm(96 + saat * 5 - int(28 * anteil)),
            _klamm(148 - int(24 * anteil)),
            _klamm(196 - int(16 * anteil)),
        )
    anteil = (y - horizont) / max(hoehe - horizont, 1)
    return (
        _klamm(176 - int(48 * anteil)),
        _klamm(148 - int(36 * anteil)),
        _klamm(104 - int(20 * anteil)),
    )


def _klamm(wert: int) -> int:
    if wert < 0:
        return 0
    if wert > 255:
        return 255
    return wert


def _png(breite: int, hoehe: int, roh: bytes) -> bytes:
    def chunk(typ: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(typ + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + typ + data + struct.pack(">I", crc)

    kopf = struct.pack(">IIBBBBB", breite, hoehe, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", kopf)
        + chunk(b"IDAT", zlib.compress(roh, 9))
        + chunk(b"IEND", b"")
    )
