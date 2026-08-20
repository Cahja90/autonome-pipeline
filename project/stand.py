"""fortschritt auf platte."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from config import kanal_ordner


def stand_pfad(kanal: str):
    return kanal_ordner(kanal) / "stand.json"


def stand_laden(kanal: str) -> dict:
    pfad = stand_pfad(kanal)
    if not pfad.is_file():
        return {
            "kanal": kanal,
            "letzter_schritt": 0,
            "schritte": {},
            "halt": False,
        }
    return json.loads(pfad.read_text(encoding="utf-8"))


def stand_speichern(kanal: str, daten: dict) -> None:
    ordner = kanal_ordner(kanal)
    ordner.mkdir(parents=True, exist_ok=True)
    daten["zeit"] = datetime.now(timezone.utc).isoformat()
    stand_pfad(kanal).write_text(
        json.dumps(daten, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def schritt_merken(kanal: str, nummer: int, status: str, extra: dict | None = None) -> dict:
    daten = stand_laden(kanal)
    daten["letzter_schritt"] = max(int(daten.get("letzter_schritt") or 0), nummer)
    daten.setdefault("schritte", {})
    eintrag = {"status": status}
    if extra:
        eintrag["extra"] = extra
    daten["schritte"][str(nummer)] = eintrag
    stand_speichern(kanal, daten)
    return daten


def ist_halt(kanal: str) -> bool:
    if (kanal_ordner(kanal) / ".halt").is_file():
        return True
    return bool(stand_laden(kanal).get("halt"))
