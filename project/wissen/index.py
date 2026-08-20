"""texte in stuecke legen."""

from __future__ import annotations

import re
from pathlib import Path

from ablage import json_liste, json_schreiben
from config import kanal_ordner

CHUNK_GROESSE = 700
CHUNK_UEBERLAPP = 120
BILD_ENDUNGEN = {".jpg", ".jpeg", ".png"}


def laufen(kanal: str) -> dict:
    videos = json_liste(kanal_ordner(kanal) / "videos.json")
    orte = json_liste(kanal_ordner(kanal) / "orte.json")
    chunks = []
    for video in videos:
        video_id = video.get("video_id")
        if not video_id:
            continue
        text = _text_lesen(kanal, video_id)
        if not text.strip():
            continue
        ort = _ort_fuer(orte, video_id)
        bilder = _bilder_pfade(kanal, video_id)
        for stueck in _text_teilen(text):
            chunks.append(
                {
                    "video_id": video_id,
                    "ort": ort,
                    "text": stueck,
                    "bilder": bilder,
                }
            )
    pfad = kanal_ordner(kanal) / "wissen.json"
    json_schreiben(pfad, {"chunks": chunks})
    return {"anzahl": len(chunks), "pfad": str(pfad)}


def _text_lesen(kanal: str, video_id: str) -> str:
    pfad = kanal_ordner(kanal) / "transcripts" / video_id / "text.txt"
    if not pfad.is_file():
        return ""
    return pfad.read_text(encoding="utf-8")


def _ort_fuer(orte: list, video_id: str) -> str:
    for ort in orte:
        ids = ort.get("video_ids") or []
        if video_id in ids:
            return str(ort.get("slug") or "")
    return ""


def _bilder_pfade(kanal: str, video_id: str) -> list[str]:
    wurzel = kanal_ordner(kanal)
    ordner = wurzel / "bilder" / video_id
    if not ordner.is_dir():
        return []
    treffer = []
    for pfad in sorted(ordner.iterdir()):
        if pfad.suffix.lower() in BILD_ENDUNGEN:
            treffer.append(_rel_pfad(wurzel, pfad))
    return treffer


def _rel_pfad(wurzel: Path, pfad: Path) -> str:
    return pfad.relative_to(wurzel).as_posix()


def _text_teilen(text: str) -> list[str]:
    if not text:
        return []
    glatt = re.sub(r"\s+", " ", text.strip())
    if len(glatt) <= CHUNK_GROESSE:
        return [glatt]
    stuecke = []
    start = 0
    while start < len(glatt):
        ende = min(len(glatt), start + CHUNK_GROESSE)
        if ende < len(glatt):
            bruch = glatt.rfind(" ", start + CHUNK_GROESSE // 2, ende)
            if bruch > start:
                ende = bruch
        teil = glatt[start:ende].strip()
        if len(teil) > 80:
            stuecke.append(teil)
        if ende >= len(glatt):
            break
        start = max(ende - CHUNK_UEBERLAPP, start + 1)
    return stuecke
