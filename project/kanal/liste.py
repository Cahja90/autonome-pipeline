"""videoliste vom kanal holen."""

from __future__ import annotations

import json
import os
import subprocess

from ablage import json_liste, json_schreiben
from config import PROJECT_DIR, kanal_ordner


def laufen(kanal_url: str, kanal: str) -> dict:
    videos = _videos_laden(kanal_url)
    pfad = kanal_ordner(kanal) / "videos.json"
    json_schreiben(pfad, videos)
    return {"anzahl": len(videos), "pfad": str(pfad)}


def _ist_beispiel(kanal_url: str) -> bool:
    if os.environ.get("CHANNEL_SITE_BEISPIEL") == "1":
        return True
    return (kanal_url or "").strip() == "beispiel"


def _videos_laden(kanal_url: str) -> list:
    if _ist_beispiel(kanal_url):
        return json_liste(PROJECT_DIR / "beispiel" / "videos.json")
    return _videos_von_yt(kanal_url)


def _videos_von_yt(kanal_url: str) -> list:
    daten = _yt_json(kanal_url)
    eintraege = daten.get("entries")
    if not isinstance(eintraege, list):
        eintraege = [daten]
    videos = []
    for eintrag in eintraege:
        video = _video_aus_eintrag(eintrag)
        if video:
            videos.append(video)
    return videos


def _video_aus_eintrag(eintrag: dict | None) -> dict | None:
    if not eintrag:
        return None
    video_id = eintrag.get("id")
    if not video_id:
        return None
    titel = eintrag.get("title") or video_id
    url = eintrag.get("url") or ""
    if not str(url).startswith("http"):
        url = f"https://www.youtube.com/watch?v={video_id}"
    return {"video_id": video_id, "title": titel, "url": url}


def _yt_json(kanal_url: str) -> dict:
    befehl = [
        "yt-dlp",
        "--flat-playlist",
        "-J",
        "--no-warnings",
        kanal_url,
    ]
    try:
        fertig = subprocess.run(
            befehl,
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as err:
        raise RuntimeError("yt-dlp fehlt") from err
    except subprocess.CalledProcessError as err:
        extra = (err.stderr or err.stdout or "").strip()
        raise RuntimeError(f"yt-dlp fehlgeschlagen: {extra}") from err
    return json.loads(fertig.stdout)
