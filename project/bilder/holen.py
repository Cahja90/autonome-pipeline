"""standbilder aus videos."""

from __future__ import annotations

import base64
import os
import shutil
import subprocess
from pathlib import Path

from ablage import json_liste
from config import DEFAULT_FPS_EVERY, PROJECT_DIR, kanal_ordner

#kleines png, 67 byte
PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACklEQVR4n"
    "GMAAQAABQABDQottAAAAABJRU5ErkJggg=="
)


def laufen(kanal: str) -> dict:
    videos = json_liste(kanal_ordner(kanal) / "videos.json")
    fertig = 0
    for video in videos:
        if _eins(kanal, video):
            fertig += 1
    pfad = kanal_ordner(kanal) / "bilder"
    return {"anzahl": fertig, "pfad": str(pfad)}


def _ist_beispiel(kanal: str) -> bool:
    if os.environ.get("CHANNEL_SITE_BEISPIEL") == "1":
        return True
    return kanal == "beispiel"


def _eins(kanal: str, video: dict) -> bool:
    video_id = video.get("video_id")
    if not video_id:
        return False
    ziel_ordner = kanal_ordner(kanal) / "bilder" / video_id
    ziel_ordner.mkdir(parents=True, exist_ok=True)
    if _ist_beispiel(kanal):
        _beispiel_bild(ziel_ordner / "frame_001.png")
        return True
    _ffmpeg_oder_bruch()
    video_pfad = _video_bereit(kanal, video)
    _frames_schneiden(video_pfad, ziel_ordner)
    return True


def _beispiel_bild(ziel: Path) -> None:
    quelle = _png_sichern()
    shutil.copy2(quelle, ziel)


def _png_sichern() -> Path:
    quelle = PROJECT_DIR / "beispiel" / "bild.png"
    quelle.parent.mkdir(parents=True, exist_ok=True)
    if not quelle.is_file() or quelle.stat().st_size < 8:
        quelle.write_bytes(PNG_1X1)
    return quelle


def _ffmpeg_oder_bruch() -> None:
    if shutil.which("ffmpeg"):
        return
    raise RuntimeError("ffmpeg fehlt")


def _video_bereit(kanal: str, video: dict) -> Path:
    video_id = video["video_id"]
    pfad = kanal_ordner(kanal) / "videos" / f"{video_id}.mp4"
    if pfad.is_file():
        return pfad
    url = (video.get("url") or "").strip()
    if not url.startswith("http"):
        url = f"https://www.youtube.com/watch?v={video_id}"
    _yt_laden(url, pfad)
    if not pfad.is_file():
        raise RuntimeError(f"video fehlt: {pfad}")
    return pfad


def _yt_laden(url: str, ziel: Path) -> None:
    ziel.parent.mkdir(parents=True, exist_ok=True)
    befehl = ["yt-dlp", "-o", str(ziel), "--no-playlist", "--", url]
    try:
        subprocess.run(
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


def _frames_schneiden(video_pfad: Path, ziel_ordner: Path) -> None:
    befehl = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_pfad),
        "-vf",
        f"fps=1/{DEFAULT_FPS_EVERY}",
        str(ziel_ordner / "frame_%03d.jpg"),
    ]
    try:
        subprocess.run(
            befehl,
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as err:
        raise RuntimeError("ffmpeg fehlt") from err
    except subprocess.CalledProcessError as err:
        extra = (err.stderr or err.stdout or "").strip()
        raise RuntimeError(f"ffmpeg fehlgeschlagen: {extra}") from err
