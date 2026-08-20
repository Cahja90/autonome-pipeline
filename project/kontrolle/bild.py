"""bild pruefen ohne pil."""

from __future__ import annotations

from pathlib import Path

import config

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff"
IHDR = b"IHDR"
_KOPF = 65_536


def bild_ok(pfad: Path) -> tuple[bool, str]:
    if not pfad.is_file():
        return False, "fehlt"
    groesse = pfad.stat().st_size
    if groesse < config.MIN_FRAME_BYTES:
        return False, "zu klein"
    with pfad.open("rb") as datei:
        kopf = datei.read(_KOPF)
    if kopf.startswith(PNG_MAGIC):
        return _png_ok(pfad.name, kopf)
    if kopf.startswith(JPEG_MAGIC):
        return True, "ok"
    return False, "kein png/jpeg"


def _png_ok(name: str, daten: bytes) -> tuple[bool, str]:
    masse = _ihdr_masse(daten)
    if masse is None:
        return False, "kein ihdr"
    breite, hoehe = masse
    minst = _min_px(name)
    if breite < minst or hoehe < minst:
        return False, "zu klein in pixel"
    return True, "ok"


def _min_px(name: str) -> int:
    klein = name.lower()
    if klein.startswith("pano") or klein.startswith("world_"):
        return config.MIN_PANO_PX
    return 1


def _ihdr_masse(daten: bytes) -> tuple[int, int] | None:
    pos = 8
    while pos + 8 <= len(daten):
        laenge = int.from_bytes(daten[pos : pos + 4], "big")
        typ = daten[pos + 4 : pos + 8]
        start = pos + 8
        ende = start + laenge
        if ende > len(daten):
            break
        if typ == IHDR and laenge >= 8:
            breite = int.from_bytes(daten[start : start + 4], "big")
            hoehe = int.from_bytes(daten[start + 4 : start + 8], "big")
            return breite, hoehe
        pos = ende + 4
    return None
