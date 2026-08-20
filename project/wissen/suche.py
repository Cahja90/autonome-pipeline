"""stuecke zur frage finden."""

from __future__ import annotations

from ablage import json_lesen
from config import kanal_ordner


def suchen(kanal: str, frage: str, limit: int = 8) -> list[dict]:
    daten = json_lesen(kanal_ordner(kanal) / "wissen.json")
    chunks = daten.get("chunks") or []
    woerter = _frage_woerter(frage)
    if not woerter:
        return []
    treffer = []
    for chunk in chunks:
        score = _score(chunk.get("text") or "", woerter)
        if score <= 0:
            continue
        eintrag = dict(chunk)
        eintrag["score"] = score
        treffer.append(eintrag)
    treffer.sort(key=lambda item: item["score"], reverse=True)
    return treffer[:limit]


def _frage_woerter(frage: str) -> list[str]:
    teile = (frage or "").strip().split()
    return [teil.lower() for teil in teile if len(teil) >= 2]


def _score(text: str, woerter: list[str]) -> int:
    klein = text.lower()
    return sum(klein.count(wort) for wort in woerter)
