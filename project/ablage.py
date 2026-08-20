"""json auf platte."""

from __future__ import annotations

import json
from pathlib import Path


def json_lesen(pfad: Path, leer: dict | None = None) -> dict:
    if not pfad.is_file():
        return {} if leer is None else dict(leer)
    return json.loads(pfad.read_text(encoding="utf-8"))


def json_schreiben(pfad: Path, daten: dict | list) -> None:
    pfad.parent.mkdir(parents=True, exist_ok=True)
    pfad.write_text(
        json.dumps(daten, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def json_liste(pfad: Path) -> list:
    if not pfad.is_file():
        return []
    roh = json.loads(pfad.read_text(encoding="utf-8"))
    if not isinstance(roh, list):
        raise ValueError(f"keine liste: {pfad}")
    return roh
