"""grundriss vor blender. eine quelle fuer bauen und pruefen."""

from __future__ import annotations

MIN_TUEREN = 2
MAX_TUEREN = 4
WAND_Y = 10.0
WAND_Z = 4.5
WAND_TIEFE = 1.0
HALBE_BREITE = 12.0
TUER_BREITE = 2.2
TUER_HOEHE = 3.0


def ort_plan(ort: dict) -> dict:
    slug = (ort.get("slug") or "ort").strip().lower()
    name = ort.get("name") or slug
    anzahl = _tuer_zahl(ort.get("oeffnungen"))
    tueren = _tuer_reihe(anzahl)
    return {
        "slug": slug,
        "name": name,
        "wand_y": WAND_Y,
        "wand_z": WAND_Z,
        "tuer_hoehe": TUER_HOEHE,
        "tueren": tueren,
        "waende_block": _block_punkte(tueren),
        "prompt": (
            f"Photorealistic ancient site {name}. Use uploaded GLB as structure. "
            "Preserve openings. Weathered stone. No text, no people."
        ),
    }


def _tuer_zahl(wert) -> int:
    try:
        zahl = int(wert)
    except (TypeError, ValueError):
        zahl = MIN_TUEREN
    return max(MIN_TUEREN, min(MAX_TUEREN, zahl))


def _tuer_reihe(anzahl: int) -> list[dict]:
    span = HALBE_BREITE * 2
    stueck = span / (anzahl + 1)
    tueren = []
    for i in range(anzahl):
        x = -HALBE_BREITE + stueck * (i + 1)
        tueren.append(
            {
                "name": f"tuer_{i + 1}",
                "x": round(x, 3),
                "y": WAND_Y,
                "breite": TUER_BREITE,
            }
        )
    return tueren


def _block_punkte(tueren: list[dict]) -> list[dict]:
    xs = sorted(t["x"] for t in tueren)
    mitte = (xs[0] + xs[-1]) / 2 if xs else 0.0
    #punkt zwischen tueren, wand muss treffen
    if len(xs) >= 2:
        mitte = (xs[0] + xs[1]) / 2
    return [{"name": "wand_mitte", "x": round(mitte, 3), "y": WAND_Y}]
