"""screenshot lesen und gegen referenzen halten."""

from __future__ import annotations

import json
import os
import subprocess
import zlib
from pathlib import Path

import config
from kontrolle.bild import IHDR, PNG_MAGIC, bild_ok

MAX_ABSTAND = 40.0
PNG_RGB = 2
PNG_RGBA = 6


def sicht_pruefen(shot: Path, refs: list[Path] | None = None) -> dict:
    gut, grund = bild_ok(shot)
    if not gut:
        return {
            "ok": False,
            "grund": grund,
            "aenderung": "neu_shot",
            "datei": shot.name,
        }
    hell = png_helligkeit(shot)
    if hell is None:
        return {
            "ok": False,
            "grund": "bild nicht lesbar",
            "aenderung": "neu_shot",
            "datei": shot.name,
        }
    if hell < config.BLACK_MEAN_MAX:
        return _bericht(shot, False, "zu dunkel", "kamera_hoch", hell)
    if hell > config.WHITE_MEAN_MIN:
        return _bericht(shot, False, "zu hell", "kamera_runter", hell)
    refs = refs or []
    ziel = _ref_hell(refs)
    if ziel is not None:
        if hell + MAX_ABSTAND < ziel:
            return _bericht(shot, False, "dunkler als referenz", "kamera_hoch", hell)
        if hell - MAX_ABSTAND > ziel:
            return _bericht(shot, False, "heller als referenz", "kamera_runter", hell)
    ki = ki_sicht(shot, refs)
    if ki is not None:
        ki.setdefault("hell", hell)
        ki.setdefault("datei", shot.name)
        return ki
    return _bericht(shot, True, "ok", "ok", hell)


def png_helligkeit(pfad: Path) -> float | None:
    roh = pfad.read_bytes()
    if not roh.startswith(PNG_MAGIC):
        return None
    masse = _ihdr(roh)
    if masse is None:
        return None
    breite, hoehe, farbe = masse
    roh_pixel = _idat(roh)
    if roh_pixel is None:
        return None
    werte = _pixel_mittel(roh_pixel, breite, hoehe, farbe)
    if not werte:
        return None
    return sum(werte) / len(werte)


def ki_sicht(shot: Path, refs: list[Path]) -> dict | None:
    befehl = os.environ.get("CHANNEL_SITE_SICHT_CMD", "").strip()
    if not befehl:
        return None
    args = befehl.split() + [str(shot), *[str(p) for p in refs]]
    fertig = subprocess.run(args, capture_output=True, text=True, check=False)
    if fertig.returncode != 0:
        extra = (fertig.stderr or fertig.stdout or "").strip()
        return {
            "ok": False,
            "grund": extra or "sicht-befehl fehlgeschlagen",
            "aenderung": "prompt_oeffnungen",
            "datei": shot.name,
        }
    try:
        daten = json.loads(fertig.stdout)
    except json.JSONDecodeError as err:
        raise RuntimeError(f"sicht-befehl keine json: {err}") from err
    if not isinstance(daten, dict):
        raise RuntimeError("sicht-befehl: json ist kein objekt")
    return daten


def _bericht(shot: Path, ok: bool, grund: str, aenderung: str, hell: float) -> dict:
    return {
        "ok": ok,
        "grund": grund,
        "aenderung": aenderung,
        "hell": round(hell, 2),
        "datei": shot.name,
    }


def _ref_hell(refs: list[Path]) -> float | None:
    werte = []
    for pfad in refs:
        if not pfad.is_file():
            continue
        hell = png_helligkeit(pfad)
        if hell is not None:
            werte.append(hell)
    if not werte:
        return None
    return sum(werte) / len(werte)


def _ihdr(daten: bytes) -> tuple[int, int, int] | None:
    pos = 8
    while pos + 8 <= len(daten):
        laenge = int.from_bytes(daten[pos : pos + 4], "big")
        typ = daten[pos + 4 : pos + 8]
        start = pos + 8
        ende = start + laenge
        if ende > len(daten):
            break
        if typ == IHDR and laenge >= 9:
            breite = int.from_bytes(daten[start : start + 4], "big")
            hoehe = int.from_bytes(daten[start + 4 : start + 8], "big")
            farbe = daten[start + 9]
            return breite, hoehe, farbe
        pos = ende + 4
    return None


def _idat(daten: bytes) -> bytes | None:
    teile = []
    pos = 8
    while pos + 8 <= len(daten):
        laenge = int.from_bytes(daten[pos : pos + 4], "big")
        typ = daten[pos + 4 : pos + 8]
        start = pos + 8
        ende = start + laenge
        if ende > len(daten):
            break
        if typ == b"IDAT":
            teile.append(daten[start:ende])
        pos = ende + 4
    if not teile:
        return None
    return zlib.decompress(b"".join(teile))


def _pixel_mittel(roh: bytes, breite: int, hoehe: int, farbe: int) -> list[float]:
    kanaele = 3 if farbe == PNG_RGB else 4 if farbe == PNG_RGBA else 0
    if kanaele == 0 or breite < 1 or hoehe < 1:
        return []
    zeile = 1 + breite * kanaele
    hell = []
    pos = 0
    for _ in range(hoehe):
        if pos + zeile > len(roh):
            break
        #filterbyte ueberspringen, rohwerte als helligkeit
        nutz = roh[pos + 1 : pos + zeile]
        pos += zeile
        for i in range(0, len(nutz) - 2, kanaele):
            hell.append((nutz[i] + nutz[i + 1] + nutz[i + 2]) / 3)
    return hell
