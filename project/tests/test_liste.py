from __future__ import annotations

import json

import config
from kanal.liste import laufen


def test_beispiel_schreibt_zwei(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "WORK_DIR", tmp_path)
    monkeypatch.setenv("CHANNEL_SITE_BEISPIEL", "1")
    ergebnis = laufen("https://www.youtube.com/@egal", "demo")
    assert ergebnis["anzahl"] == 2
    pfad = tmp_path / "demo" / "videos.json"
    videos = json.loads(pfad.read_text(encoding="utf-8"))
    assert len(videos) == 2
    for video in videos:
        assert video["video_id"]
        assert video["title"]
        assert video["url"]
