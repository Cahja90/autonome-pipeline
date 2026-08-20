"""schritt 10: 3d an orte haengen, dann seite online oder lokal."""

from __future__ import annotations

import subprocess
from pathlib import Path
from shutil import which

from ablage import json_schreiben
from config import kanal_ordner
from seite.welten import einsetzen
from stand import schritt_merken


def laufen(kanal: str) -> dict:
    seite = kanal_ordner(kanal) / "seite"
    qa = seite / "out" / "QA_PASSED.txt"
    if not qa.is_file():
        raise RuntimeError("kontrolle nicht bestanden: QA_PASSED.txt fehlt")
    if not seite.is_dir():
        raise RuntimeError("seite fehlt")
    welt_stand = einsetzen(kanal)
    wrangler = which("wrangler") or which("wrangler.cmd")
    if wrangler:
        try:
            return _online_stellen(kanal, seite, wrangler)
        except RuntimeError:
            #kein cloudflare-projekt: seite bleibt lokal. keine api-texte speichern
            daten = {
                "status": "lokal",
                "grund": "online nicht möglich, seite bleibt lokal",
                "mit_welt": welt_stand.get("mit_welt"),
            }
            json_schreiben(seite / "online.json", daten)
            json_schreiben(seite / "out" / "online.json", daten)
            schritt_merken(kanal, 10, "ok", daten)
            return {"ok": True, **daten}
    daten = {
        "status": "lokal",
        "mit_welt": welt_stand.get("mit_welt"),
    }
    json_schreiben(seite / "online.json", daten)
    json_schreiben(seite / "out" / "online.json", daten)
    schritt_merken(kanal, 10, "ok", daten)
    return {"ok": True, **daten}


def _online_stellen(kanal: str, seite: Path, wrangler: str) -> dict:
    fertig = subprocess.run(
        [
            wrangler,
            "pages",
            "deploy",
            str(seite),
            "--project-name",
            "channel-site",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if fertig.returncode != 0:
        raise RuntimeError("wrangler fehlgeschlagen")
    daten = {"status": "online", "projekt": "channel-site", "pfad": str(seite)}
    json_schreiben(seite / "online.json", daten)
    json_schreiben(seite / "out" / "online.json", daten)
    schritt_merken(kanal, 10, "ok", daten)
    return {"ok": True, **daten}
