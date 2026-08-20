"""orte aus titel und text."""

from __future__ import annotations

import re

from ablage import json_liste, json_schreiben
from config import kanal_ordner
from orte.lage import geocode

MIN_OEFFNUNG = 2
MAX_OEFFNUNG = 4
OEFFNUNG_WOERTER = (
    "tür",
    "tuer",
    "door",
    "арк",
    "arch",
    "öffnung",
    "проход",
)
KEIN_ORT = frozenset(
    {
        "rundgang",
        "uberblick",
        "überblick",
        "ueberblick",
        "this",
        "that",
        "then",
        "with",
        "from",
        "have",
        "been",
        "were",
        "will",
        "walk",
        "tour",
        "visit",
        "eine",
        "einer",
        "einem",
        "diese",
        "dieser",
        "unter",
        "dann",
        "wenn",
        "auch",
        "oder",
        "the",
        "and",
        "for",
        "das",
        "der",
        "die",
        "im",
    }
)
ORT_MUSTER = re.compile(
    r"(?:(?i:in|bei|из|в))\s+"
    r"([^\s][\w\-äöüßáéíóúàèìòùА-Яа-яёЁ]*"
    r"(?:\s+[A-ZÄÖÜА-ЯЁ][\w\-äöüßа-яё]*){0,2})"
)
GROSS_MUSTER = re.compile(
    r"\b(?:[A-ZÄÖÜ][a-zäöüß]{3,}|[А-ЯЁ][а-яё]{3,})"
    r"(?:\s+(?:[A-ZÄÖÜ][a-zäöüß]{3,}|[А-ЯЁ][а-яё]{3,})){0,2}\b"
)


def laufen(kanal: str) -> dict:
    videos = json_liste(kanal_ordner(kanal) / "videos.json")
    gruppen: dict[str, dict] = {}
    for video in videos:
        _video_einordnen(kanal, video, gruppen)
    orte = [_ort_eintrag(gruppe) for gruppe in gruppen.values()]
    orte.sort(key=lambda eintrag: eintrag["slug"])
    pfad = kanal_ordner(kanal) / "orte.json"
    json_schreiben(pfad, orte)
    return {"anzahl": len(orte), "pfad": str(pfad)}


def _video_einordnen(kanal: str, video: dict, gruppen: dict[str, dict]) -> None:
    video_id = video.get("video_id")
    if not video_id:
        return
    titel = video.get("title") or ""
    text = _text_lesen(kanal, video_id)
    gesamt = f"{titel}\n{text}"
    for name in _orte_im_text(gesamt):
        slug = _slug(name)
        if not slug:
            continue
        gruppe = gruppen.setdefault(
            slug,
            {"slug": slug, "name": name, "video_ids": [], "texte": []},
        )
        if video_id not in gruppe["video_ids"]:
            gruppe["video_ids"].append(video_id)
        gruppe["texte"].append(gesamt)


def _ort_eintrag(gruppe: dict) -> dict:
    name = gruppe["name"]
    lat, lon = geocode(name)
    gesamt = "\n".join(gruppe["texte"])
    return {
        "slug": gruppe["slug"],
        "name": name,
        "video_ids": list(gruppe["video_ids"]),
        "oeffnungen": _oeffnungen(gesamt),
        "lat": lat,
        "lon": lon,
    }


def _text_lesen(kanal: str, video_id: str) -> str:
    pfad = kanal_ordner(kanal) / "transcripts" / video_id / "text.txt"
    if not pfad.is_file():
        return ""
    return pfad.read_text(encoding="utf-8")


def _orte_im_text(text: str) -> list[str]:
    namen: list[str] = []
    for treffer in ORT_MUSTER.finditer(text):
        _name_merken(namen, treffer.group(1))
    for treffer in GROSS_MUSTER.finditer(text):
        _name_merken(namen, treffer.group(0))
    return namen


def _name_merken(namen: list[str], roh: str) -> None:
    name = " ".join((roh or "").split())
    if not name or _ist_kein_ort(name):
        return
    klein = name.lower()
    for i, alt in enumerate(namen):
        alt_k = alt.lower()
        if klein == alt_k or klein in alt_k:
            return
        if alt_k in klein:
            namen[i] = name
            return
    namen.append(name)


def _ist_kein_ort(name: str) -> bool:
    erstes = name.split()[0].lower()
    return erstes in KEIN_ORT


def _slug(name: str) -> str:
    text = name.strip().lower()
    text = (
        text.replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ß", "ss")
    )
    text = re.sub(r"[^\w]+", "-", text, flags=re.UNICODE)
    return re.sub(r"-{2,}", "-", text).strip("-")


def _oeffnungen(text: str) -> int:
    klein = text.lower()
    zahl = 0
    for wort in OEFFNUNG_WOERTER:
        zahl += klein.count(wort)
    if zahl < MIN_OEFFNUNG:
        return MIN_OEFFNUNG
    if zahl > MAX_OEFFNUNG:
        return MAX_OEFFNUNG
    return zahl
