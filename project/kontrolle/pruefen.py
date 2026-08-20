"""schritt 9: kontrolle ohne person."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from ablage import json_lesen, json_schreiben
from config import kanal_ordner
from kontrolle.bild import bild_ok
from stand import schritt_merken

_BILD_ENDUNGEN = {".png", ".jpg", ".jpeg"}


def laufen(kanal: str) -> dict:
    wurzel = kanal_ordner(kanal)
    welt_wurzel = wurzel / "welt"
    ordner_liste = _ort_ordner(welt_wurzel)
    berichte = [_ort_pruefen(ordner) for ordner in ordner_liste]
    fehler = []
    for bericht in berichte:
        fehler.extend(bericht["fehler"])
    ok = len(fehler) == 0
    ziel = wurzel / "seite" / "out"
    json_schreiben(
        ziel / "kontrolle.json",
        {"ok": ok, "orte": berichte, "fehler": fehler},
    )
    qa = ziel / "QA_PASSED.txt"
    if ok:
        #kein warten auf eine person
        qa.write_text(
            "ok\n" + datetime.now(timezone.utc).isoformat() + "\n",
            encoding="utf-8",
        )
        schritt_merken(kanal, 9, "ok", {"anzahl": len(berichte)})
    else:
        if qa.is_file():
            qa.unlink()
        schritt_merken(kanal, 9, "fehler", {"anzahl": len(fehler)})
    return {
        "ok": ok,
        "anzahl": len(berichte),
        "fehler": fehler,
        "pfad": str(ziel),
    }


def _ort_ordner(welt_wurzel: Path) -> list[Path]:
    if not welt_wurzel.is_dir():
        return []
    return sorted(p for p in welt_wurzel.iterdir() if p.is_dir())


def _ort_pruefen(ordner: Path) -> dict:
    slug = ordner.name
    fehler: list[str] = []
    verify = (ordner / "verify_ok.txt").is_file()
    if not verify:
        fehler.append(f"{slug}: verify_ok.txt fehlt")
    skip = (ordner / "skip_marble.txt").is_file() or (
        ordner / "skip_chisel.txt"
    ).is_file()
    front = ordner / "world_front.png"
    if not skip and not front.is_file():
        fehler.append(f"{slug}: world_front.png fehlt")
    sicht = json_lesen(ordner / "sicht.json", {})
    if sicht and sicht.get("ok") is False:
        fehler.append(f"{slug}: sicht nicht ok")
    bilder = []
    for pfad in _welt_bilder(ordner):
        gut, grund = bild_ok(pfad)
        bilder.append({"datei": pfad.name, "ok": gut, "grund": grund})
        if not gut:
            fehler.append(f"{slug}: {pfad.name} {grund}")
    return {
        "slug": slug,
        "ok": len(fehler) == 0,
        "verify": verify,
        "skip_marble": skip,
        "bilder": bilder,
        "fehler": fehler,
    }


def _welt_bilder(ordner: Path) -> list[Path]:
    treffer = []
    for pfad in sorted(ordner.iterdir()):
        if not pfad.is_file():
            continue
        name = pfad.name.lower()
        if pfad.suffix.lower() not in _BILD_ENDUNGEN:
            continue
        if name.startswith("world_") or name.startswith("pano"):
            treffer.append(pfad)
    return treffer
