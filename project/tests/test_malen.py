from __future__ import annotations

import struct
import zlib

from bilder.malen import szene_png


def test_szene_ist_png_ohne_text():
    roh = szene_png(saat=2)
    assert roh.startswith(b"\x89PNG\r\n\x1a\n")
    typen = _chunk_typen(roh)
    assert typen[0] == b"IHDR"
    assert typen[-1] == b"IEND"
    assert b"tEXt" not in typen
    assert b"iTXt" not in typen
    assert b"zTXt" not in typen
    breite, hoehe = _masse(roh)
    assert breite == 480
    assert hoehe == 270
    assert len(roh) > 1000


def test_zwei_saaten_sehen_anders_aus():
    assert szene_png(saat=1) != szene_png(saat=5, nah=True)


def _chunk_typen(roh: bytes) -> list[bytes]:
    typen = []
    pos = 8
    while pos + 8 <= len(roh):
        laenge = struct.unpack(">I", roh[pos : pos + 4])[0]
        typ = roh[pos + 4 : pos + 8]
        typen.append(typ)
        pos = pos + 12 + laenge
        if typ == b"IEND":
            break
    return typen


def _masse(roh: bytes) -> tuple[int, int]:
    laenge = struct.unpack(">I", roh[8:12])[0]
    assert roh[12:16] == b"IHDR"
    daten = roh[16 : 16 + laenge]
    crc = struct.unpack(">I", roh[16 + laenge : 20 + laenge])[0]
    assert crc == (zlib.crc32(b"IHDR" + daten) & 0xFFFFFFFF)
    breite, hoehe = struct.unpack(">II", daten[:8])
    return breite, hoehe
