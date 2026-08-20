from __future__ import annotations

from ablage import json_schreiben
from seite.bauen import laufen as seite_bauen
from seite.welten import einsetzen


def test_welt_kommt_an_den_ort(tmp_path, monkeypatch):
    import config

    monkeypatch.setattr(config, "WORK_DIR", tmp_path)
    kanal = "demo"
    wurzel = tmp_path / kanal
    json_schreiben(
        wurzel / "orte.json",
        [
            {
                "slug": "ostia",
                "name": "Ostia",
                "video_ids": [],
                "lat": 41.755,
                "lon": 12.291,
            }
        ],
    )
    json_schreiben(wurzel / "wissen.json", {"chunks": []})
    json_schreiben(wurzel / "videos.json", [])
    seite_bauen(kanal)
    welt = wurzel / "welt" / "ostia"
    welt.mkdir(parents=True)
    (welt / "ostia.glb").write_bytes(b"glb")
    ergebnis = einsetzen(kanal)
    assert ergebnis["mit_welt"] == 1
    html = (wurzel / "seite" / "ort" / "ostia.html").read_text(encoding="utf-8")
    assert "model-viewer" in html
    assert (wurzel / "seite" / "modelle" / "ostia.glb").is_file()
