"""ort auf der karte finden."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request

NOMINATIM = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "channel-site/0.1"
TIMEOUT_SEC = 20
OSTIA_LAGE = (41.755, 12.291)
BEISPIEL_LAGE = {
    "forum": (41.892, 12.485),
}


def geocode(name: str) -> tuple[float | None, float | None]:
    if os.environ.get("CHANNEL_SITE_BEISPIEL") == "1":
        return _beispiel_lage(name)
    return _nominatim(name)


def _beispiel_lage(name: str) -> tuple[float | None, float | None]:
    klein = (name or "").lower()
    if "ostia" in klein:
        return OSTIA_LAGE
    for schluessel, lage in BEISPIEL_LAGE.items():
        if schluessel in klein:
            return lage
    return (None, None)


def _nominatim(name: str) -> tuple[float | None, float | None]:
    frage = (name or "").strip()
    if not frage:
        return (None, None)
    query = urllib.parse.urlencode({"q": frage, "format": "json", "limit": "1"})
    anfrage = urllib.request.Request(
        f"{NOMINATIM}?{query}",
        headers={"User-Agent": USER_AGENT},
    )
    try:
        with urllib.request.urlopen(anfrage, timeout=TIMEOUT_SEC) as antwort:
            roh = antwort.read().decode("utf-8")
    except (urllib.error.URLError, TimeoutError, OSError):
        return (None, None)
    try:
        daten = json.loads(roh)
    except json.JSONDecodeError:
        return (None, None)
    if not daten:
        return (None, None)
    try:
        lat = float(daten[0]["lat"])
        lon = float(daten[0]["lon"])
    except (KeyError, TypeError, ValueError, IndexError):
        return (None, None)
    return (lat, lon)
