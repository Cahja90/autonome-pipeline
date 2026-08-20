from __future__ import annotations

import json

import config
from bilder.holen import laufen as bilder_laufen
from kanal.liste import laufen as liste_laufen
from kanal.transkript import laufen as transkript_laufen
from orte.finden import laufen as orte_laufen
from wissen.index import laufen
from wissen.suche import suchen


def _demo_fuellen(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "WORK_DIR", tmp_path)
    monkeypatch.setenv("CHANNEL_SITE_BEISPIEL", "1")
    liste_laufen("beispiel", "demo")
    transkript_laufen("demo")
    extra = tmp_path / "demo" / "transcripts" / "ostiawalk01" / "text.txt"
    satz = extra.read_text(encoding="utf-8").strip() + " ostia tuer. "
    extra.write_text(satz * 20, encoding="utf-8")


def test_wissen_sucht_ostia(tmp_path, monkeypatch):
    _demo_fuellen(tmp_path, monkeypatch)
    orte_laufen("demo")
    ergebnis = laufen("demo")
    assert ergebnis["anzahl"] >= 1
    pfad = tmp_path / "demo" / "wissen.json"
    daten = json.loads(pfad.read_text(encoding="utf-8"))
    chunks = daten["chunks"]
    assert chunks
    assert chunks[0]["video_id"]
    assert "text" in chunks[0]
    treffer = suchen("demo", "ostia", limit=8)
    assert treffer
    assert treffer[0]["score"] >= 1
    assert "ostia" in treffer[0]["text"].lower()


def test_wissen_haengt_bilder(tmp_path, monkeypatch):
    _demo_fuellen(tmp_path, monkeypatch)
    bilder_laufen("demo")
    orte_laufen("demo")
    laufen("demo")
    daten = json.loads((tmp_path / "demo" / "wissen.json").read_text(encoding="utf-8"))
    mit_bild = [c for c in daten["chunks"] if c["bilder"]]
    assert mit_bild
    assert mit_bild[0]["bilder"][0].endswith("frame_001.png")
    bild = tmp_path / "demo" / mit_bild[0]["bilder"][0]
    assert bild.is_file()
    ostia = [c for c in daten["chunks"] if c["ort"] == "ostia"]
    assert ostia
