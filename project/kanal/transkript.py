"""texte zu den videos holen."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

from ablage import json_liste
from config import PROJECT_DIR, kanal_ordner

_ZEIT = re.compile(
    r"\d{1,2}:\d{2}(?::\d{2})?[.,]\d{3}\s*-->\s*"
    r"\d{1,2}:\d{2}(?::\d{2})?[.,]\d{3}"
)
_TAG = re.compile(r"<[^>]+>")
_NUMMER = re.compile(r"^\d+$")


def laufen(kanal: str) -> dict:
    videos = json_liste(kanal_ordner(kanal) / "videos.json")
    done = 0
    skip = 0
    for video in videos:
        if _eins_schreiben(kanal, video):
            done += 1
        else:
            skip += 1
    return {"done": done, "skip": skip}


def _eins_schreiben(kanal: str, video: dict) -> bool:
    video_id = video.get("video_id")
    if not video_id:
        return False
    ziel = kanal_ordner(kanal) / "transcripts" / video_id / "text.txt"
    if ziel.is_file():
        return True
    if _ist_beispiel(kanal):
        _aus_beispiel(video_id, ziel)
        return True
    return _aus_netz(kanal, video, ziel)


def _ist_beispiel(kanal: str) -> bool:
    if os.environ.get("CHANNEL_SITE_BEISPIEL") == "1":
        return True
    return kanal == "beispiel"


def _aus_beispiel(video_id: str, ziel: Path) -> None:
    quelle = PROJECT_DIR / "beispiel" / "transkripte" / f"{video_id}.txt"
    if not quelle.is_file():
        raise FileNotFoundError(f"beispiel-text fehlt: {quelle}")
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(quelle.read_text(encoding="utf-8"), encoding="utf-8")


def _aus_netz(kanal: str, video: dict, ziel: Path) -> bool:
    url = _video_adresse(video)
    ordner = ziel.parent
    ordner.mkdir(parents=True, exist_ok=True)
    _yt_untertitel(url, kanal_ordner(kanal))
    datei = _untertitel_datei(ordner)
    if datei is None:
        return False
    text = zeit_weg(datei.read_text(encoding="utf-8", errors="replace"))
    if not text.strip():
        return False
    ziel.write_text(text, encoding="utf-8")
    return True


def _video_adresse(video: dict) -> str:
    url = (video.get("url") or "").strip()
    if url.startswith("http"):
        return url
    return f"https://www.youtube.com/watch?v={video['video_id']}"


def _yt_untertitel(url: str, arbeit: Path) -> None:
    befehl = [
        "yt-dlp",
        "--skip-download",
        "--write-auto-sub",
        "--sub-langs",
        "en.*,de.*,ru.*",
        "-o",
        "transcripts/%(id)s/video",
        url,
    ]
    try:
        subprocess.run(
            befehl,
            check=True,
            capture_output=True,
            text=True,
            cwd=str(arbeit),
        )
    except FileNotFoundError as err:
        raise RuntimeError("yt-dlp fehlt") from err
    except subprocess.CalledProcessError as err:
        extra = (err.stderr or err.stdout or "").strip()
        raise RuntimeError(f"yt-dlp fehlgeschlagen: {extra}") from err


def _untertitel_datei(ordner: Path) -> Path | None:
    treffer = list(ordner.glob("*.vtt")) + list(ordner.glob("*.srt"))
    if not treffer:
        return None
    return treffer[0]


def zeit_weg(roh: str) -> str:
    #zeitmarken und klammern raus
    zeilen = []
    letzte = ""
    for roh_zeile in roh.splitlines():
        zeile = roh_zeile.strip()
        if not zeile or _ist_muell(zeile):
            continue
        text = _TAG.sub("", zeile).strip()
        if not text or text == letzte:
            continue
        zeilen.append(text)
        letzte = text
    if not zeilen:
        return ""
    return "\n".join(zeilen) + "\n"


def _ist_muell(zeile: str) -> bool:
    oben = zeile.upper()
    if oben.startswith("WEBVTT") or oben.startswith("NOTE"):
        return True
    if oben.startswith("KIND:") or oben.startswith("LANGUAGE:"):
        return True
    if _NUMMER.match(zeile):
        return True
    if _ZEIT.search(zeile):
        return True
    return False
