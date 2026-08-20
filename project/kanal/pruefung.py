"""stand der texte prüfen."""

from __future__ import annotations

from ablage import json_liste, json_schreiben
from config import kanal_ordner


def laufen(kanal: str) -> dict:
    videos = json_liste(kanal_ordner(kanal) / "videos.json")
    fertig = []
    offen = []
    for video in videos:
        video_id = video.get("video_id")
        if not video_id:
            continue
        if _hat_text(kanal, video_id):
            fertig.append(video_id)
        else:
            offen.append(video_id)
    pfad = kanal_ordner(kanal) / "pruefung.json"
    daten = {
        "fertig": fertig,
        "offen": offen,
        "anzahl_fertig": len(fertig),
        "anzahl_offen": len(offen),
        "pfad": str(pfad),
    }
    json_schreiben(pfad, daten)
    return daten


def _hat_text(kanal: str, video_id: str) -> bool:
    pfad = kanal_ordner(kanal) / "transcripts" / video_id / "text.txt"
    return pfad.is_file()
