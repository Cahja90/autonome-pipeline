"""schritt 10a: 3d-welten an die orte auf der seite haengen."""

from __future__ import annotations

from ablage import json_lesen, json_liste
from config import kanal_ordner
from seite.bauen import _ort_seite


def einsetzen(kanal: str) -> dict:
    wurzel = kanal_ordner(kanal)
    ziel = wurzel / "seite"
    if not ziel.is_dir():
        raise RuntimeError("seite fehlt — zuerst schritt 7")
    orte = json_liste(wurzel / "orte.json")
    wissen = json_lesen(wurzel / "wissen.json", {"chunks": []})
    chunks = wissen.get("chunks") or [] if isinstance(wissen, dict) else []
    videos = {v.get("video_id"): v for v in json_liste(wurzel / "videos.json")}
    gesetzt = 0
    for ort in orte:
        slug = ort.get("slug") or ""
        welt = wurzel / "welt" / slug
        _ort_seite(wurzel, ziel, ort, chunks, videos)
        if welt.is_dir() and (
            list(welt.glob("*.glb")) or list(welt.glob("world_*.png"))
        ):
            gesetzt += 1
    return {"anzahl": len(orte), "mit_welt": gesetzt, "pfad": str(ziel)}
