from __future__ import annotations

from ablage import json_schreiben


def test_beispiel_startet_blender_nicht(tmp_path, monkeypatch):
    import config
    from welt.laufen import laufen

    monkeypatch.setattr(config, "WORK_DIR", tmp_path)
    monkeypatch.setenv("CHANNEL_SITE_BEISPIEL", "1")

    def _nicht_starten(*_args, **_kwargs):
        raise AssertionError("beispiel darf nichts starten")

    monkeypatch.setattr("welt.laufen.subprocess.run", _nicht_starten)
    monkeypatch.setattr("welt.laufen.which", lambda _name: "blender.exe")
    json_schreiben(
        tmp_path / "beispiel" / "orte.json",
        [{"slug": "platz", "name": "platz", "oeffnungen": 2, "video_ids": []}],
    )
    ergebnis = laufen("beispiel")
    assert ergebnis["orte"][0]["blender"] is False
    ordner = tmp_path / "beispiel" / "welt" / "platz"
    assert (ordner / "sicht_beispiel.png").is_file()
    assert (ordner / "skip_marble.txt").is_file()
    assert "gemalt" in (ordner / "verify_ok.txt").read_text(encoding="utf-8")


def test_beispiel_geht_nicht_online(tmp_path, monkeypatch):
    import config
    from online.stellen import laufen

    monkeypatch.setattr(config, "WORK_DIR", tmp_path)
    monkeypatch.setenv("CHANNEL_SITE_BEISPIEL", "1")

    def _nicht_starten(*_args, **_kwargs):
        raise AssertionError("beispiel darf nicht online")

    monkeypatch.setattr("online.stellen.subprocess.run", _nicht_starten)
    monkeypatch.setattr("online.stellen.which", lambda _name: "wrangler.cmd")
    wurzel = tmp_path / "beispiel"
    json_schreiben(wurzel / "orte.json", [])
    json_schreiben(wurzel / "wissen.json", {"chunks": []})
    json_schreiben(wurzel / "videos.json", [])
    (wurzel / "seite" / "out").mkdir(parents=True)
    (wurzel / "seite" / "out" / "QA_PASSED.txt").write_text("ok\n", encoding="utf-8")
    ergebnis = laufen("beispiel")
    assert ergebnis["status"] == "lokal"
    assert "beispiel" in ergebnis["grund"]


def test_plan_nennt_das_welt_modell(monkeypatch):
    monkeypatch.setattr("welt.plan.MARBLE_MODELL", "marble-1.1")
    from welt.plan import ort_plan

    plan = ort_plan({"slug": "platz", "name": "platz", "oeffnungen": 2})
    assert plan["modell"] == "marble-1.1"
    assert "people" in plan["prompt"]
