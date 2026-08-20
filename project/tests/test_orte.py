from __future__ import annotations

import json

import config
from kanal.liste import laufen as liste_laufen
from kanal.transkript import laufen as transkript_laufen
from orte.finden import laufen
from orte.lage import geocode


def test_lage_beispiel(monkeypatch):
    monkeypatch.setenv("CHANNEL_SITE_BEISPIEL", "1")
    assert geocode("Ostia Antica") == (41.755, 12.291)
    lat, lon = geocode("Forum Romanum")
    assert lat == 41.892
    assert lon == 12.485
    assert geocode("Nirgends") == (None, None)


def test_orte_aus_beispiel(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "WORK_DIR", tmp_path)
    monkeypatch.setenv("CHANNEL_SITE_BEISPIEL", "1")
    liste_laufen("beispiel", "demo")
    transkript_laufen("demo")
    ergebnis = laufen("demo")
    assert ergebnis["anzahl"] >= 2
    pfad = tmp_path / "demo" / "orte.json"
    orte = json.loads(pfad.read_text(encoding="utf-8"))
    nach_slug = {ort["slug"]: ort for ort in orte}
    assert "ostia" in nach_slug
    assert "forum" in nach_slug
    assert nach_slug["ostia"]["lat"] == 41.755
    assert nach_slug["ostia"]["lon"] == 12.291
    assert nach_slug["forum"]["lat"] == 41.892
    assert nach_slug["forum"]["lon"] == 12.485
    assert "ostiawalk01" in nach_slug["ostia"]["video_ids"]
    assert "forumtour02" in nach_slug["forum"]["video_ids"]
    for ort in orte:
        assert 2 <= ort["oeffnungen"] <= 4
        assert "lat" in ort
        assert "lon" in ort


def test_oeffnungen_grenze(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "WORK_DIR", tmp_path)
    monkeypatch.setenv("CHANNEL_SITE_BEISPIEL", "1")
    ordner = tmp_path / "demo"
    videos = [
        {
            "video_id": "doorclip01",
            "title": "Tueren in Ostia",
            "url": "https://www.youtube.com/watch?v=doorclip01",
        }
    ]
    (ordner / "transcripts" / "doorclip01").mkdir(parents=True)
    (ordner / "videos.json").write_text(
        json.dumps(videos, ensure_ascii=False),
        encoding="utf-8",
    )
    text = "door arch tür tuer öffnung проход арк extra door"
    (ordner / "transcripts" / "doorclip01" / "text.txt").write_text(
        text,
        encoding="utf-8",
    )
    laufen("demo")
    orte = json.loads((ordner / "orte.json").read_text(encoding="utf-8"))
    ostia = next(ort for ort in orte if ort["slug"] == "ostia")
    assert ostia["oeffnungen"] == 4
