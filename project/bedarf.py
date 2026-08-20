"""was da ist, was fehlt. der mensch sieht es."""

from __future__ import annotations

import os
import socket
from shutil import which

from config import WORLD_ROOT

CDP_PORT = 9222


def status(beispiel: bool = False) -> dict:
    return {
        "python": True,
        "yt_dlp": _da("yt-dlp") or _da("yt-dlp.exe"),
        "ffmpeg": _da("ffmpeg"),
        "blender": _da("blender") or _da("blender.exe"),
        "cdp": _port(CDP_PORT),
        "wrangler": _da("wrangler") or _da("wrangler.cmd"),
        "chisel_skript": (WORLD_ROOT / "scripts" / "marble_chisel.py").is_file(),
        "beispiel": beispiel or os.environ.get("CHANNEL_SITE_BEISPIEL") == "1",
    }


def fehlt(daten: dict | None = None, *, beispiel: bool = False, bis: int = 10) -> list[dict]:
    daten = daten or status(beispiel=beispiel)
    liste = []
    if bis >= 1 and not daten["beispiel"] and not daten["yt_dlp"]:
        liste.append(_eintrag("yt-dlp", "videos und texte vom kanal", True))
    if bis >= 4 and not daten["ffmpeg"] and not daten["beispiel"]:
        liste.append(_eintrag("ffmpeg", "bilder aus videos", True))
    if bis >= 8 and not daten["blender"] and not daten["beispiel"]:
        liste.append(
            _eintrag("blender", "3d-grundriss vor chisel", True)
        )
    if bis >= 8 and not daten["cdp"] and not daten["beispiel"]:
        liste.append(
            _eintrag(
                "chrome cdp (port 9222)",
                "chisel live, screenshots",
                False,
            )
        )
    if bis >= 8 and not daten["chisel_skript"] and not daten["beispiel"]:
        liste.append(
            _eintrag(
                "chisel-skript",
                "ordner antike-3d-world-pipeline oder CHANNEL_SITE_WORLD_ROOT",
                False,
            )
        )
    if bis >= 10 and not daten["wrangler"]:
        liste.append(
            _eintrag("wrangler", "seite online (sonst bleibt lokal)", False)
        )
    return liste


def text_fuer_mensch(daten: dict, luecken: list[dict]) -> str:
    zeilen = ["stand der werkzeuge:"]
    zeilen.append(_zeile("yt-dlp", daten["yt_dlp"]))
    zeilen.append(_zeile("ffmpeg", daten["ffmpeg"]))
    zeilen.append(_zeile("blender", daten["blender"]))
    zeilen.append(_zeile("chrome cdp 9222", daten["cdp"]))
    zeilen.append(_zeile("wrangler", daten["wrangler"]))
    zeilen.append(_zeile("chisel-skript", daten["chisel_skript"]))
    if not luecken:
        zeilen.append("alles da, was dieser lauf braucht.")
        return "\n".join(zeilen)
    zeilen.append("")
    zeilen.append("fehlt — bitte einrichten:")
    for item in luecken:
        hart = "muss" if item["muss"] else "kann"
        zeilen.append(f"- {item['name']} ({hart}): {item['wozu']}")
    return "\n".join(zeilen)


def hart_fehlt(luecken: list[dict]) -> bool:
    return any(item["muss"] for item in luecken)


def _eintrag(name: str, wozu: str, muss: bool) -> dict:
    return {"name": name, "wozu": wozu, "muss": muss}


def _zeile(name: str, da: bool) -> str:
    marke = "da" if da else "fehlt"
    return f"- {name}: {marke}"


def _da(name: str) -> bool:
    return which(name) is not None


def _port(nummer: int) -> bool:
    try:
        sock = socket.create_connection(("127.0.0.1", nummer), timeout=0.3)
        sock.close()
        return True
    except OSError:
        return False
