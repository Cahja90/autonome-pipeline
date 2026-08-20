"""schritt 7: grundriss, blender, pruefen, dann marble."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from shutil import which

from ablage import json_liste, json_schreiben
from config import kanal_ordner
from welt.chisel import chisel_laufen
from welt.plan import ort_plan
from welt.pruefen import pruef_schreiben
from welt.skript import skript_schreiben

BILD_ENDUNGEN = {".jpg", ".jpeg", ".png"}


def laufen(kanal: str) -> dict:
    orte = json_liste(kanal_ordner(kanal) / "orte.json")
    ergebnisse = []
    for ort in orte:
        ergebnisse.append(_ort_bauen(kanal, ort))
    pfad = kanal_ordner(kanal) / "welt" / "stand.json"
    json_schreiben(pfad, {"orte": ergebnisse})
    return {"anzahl": len(ergebnisse), "orte": ergebnisse}


def _ort_bauen(kanal: str, ort: dict) -> dict:
    plan = ort_plan(ort)
    slug = plan["slug"]
    ordner = kanal_ordner(kanal) / "welt" / slug
    ordner.mkdir(parents=True, exist_ok=True)
    json_schreiben(ordner / "plan.json", plan)
    skript = skript_schreiben(plan, ordner)
    pruef = pruef_schreiben(plan, ordner)
    _referenzen(kanal, ort, ordner)
    blender = _blender_bin()
    if not blender:
        _ohne_blender(kanal, ordner)
        return {"slug": slug, "status": "skript", "blender": False}
    _blender_lauf(blender, skript)
    ok = _verify_lauf(blender, pruef, ordner)
    if not ok:
        return {"slug": slug, "status": "verify_fail", "blender": True}
    (ordner / "verify_ok.txt").write_text("VERIFY OK\n", encoding="utf-8")
    chisel = chisel_laufen(ordner, plan["prompt"])
    return {"slug": slug, "status": chisel.get("status"), "chisel": chisel, "blender": True}


def _ohne_blender(kanal: str, ordner: Path) -> None:
    (ordner / "blender_fehlt.txt").write_text("blender nicht gefunden\n", encoding="utf-8")
    (ordner / "skip_marble.txt").write_text("kein blender, kein marble\n", encoding="utf-8")
    if os.environ.get("CHANNEL_SITE_BEISPIEL") == "1" or kanal == "beispiel":
        #beispiel ohne blender: nur skripte, seite trotzdem
        (ordner / "verify_ok.txt").write_text(
            "beispiel: blender fehlt, skripte liegen\n",
            encoding="utf-8",
        )


def _referenzen(kanal: str, ort: dict, ziel: Path) -> None:
    refs = ziel / "referenzen"
    refs.mkdir(parents=True, exist_ok=True)
    kopiert = 0
    for video_id in ort.get("video_ids") or []:
        quelle = kanal_ordner(kanal) / "bilder" / video_id
        if not quelle.is_dir():
            continue
        for datei in sorted(quelle.iterdir()):
            if datei.suffix.lower() not in BILD_ENDUNGEN:
                continue
            shutil.copy2(datei, refs / f"{video_id}_{datei.name}")
            kopiert += 1
            if kopiert >= 5:
                return


def _blender_bin() -> str | None:
    for name in ("blender", "blender.exe"):
        treffer = which(name)
        if treffer:
            return treffer
    return None


def _blender_lauf(blender: str, skript: Path) -> None:
    fertig = subprocess.run(
        [blender, "-b", "-P", str(skript)],
        capture_output=True,
        text=True,
    )
    text = (fertig.stdout or "") + (fertig.stderr or "")
    if fertig.returncode != 0 or "EXPORT_OK" not in text:
        raise RuntimeError(f"blender export fehlgeschlagen: {text[-2000:]}")


def _verify_lauf(blender: str, skript: Path, ordner: Path) -> bool:
    fertig = subprocess.run(
        [blender, "-b", "-P", str(skript)],
        capture_output=True,
        text=True,
        cwd=str(ordner),
    )
    text = (fertig.stdout or "") + (fertig.stderr or "")
    (ordner / "verify_log.txt").write_text(text, encoding="utf-8")
    return fertig.returncode == 0 and "VERIFY OK" in text
