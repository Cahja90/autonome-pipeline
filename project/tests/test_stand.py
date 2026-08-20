from __future__ import annotations

from stand import ist_halt, schritt_merken, stand_laden


def test_schritt_landet(tmp_path, monkeypatch):
    import config

    monkeypatch.setattr(config, "WORK_DIR", tmp_path)
    schritt_merken("demo", 1, "ok", {"videos": 2})
    daten = stand_laden("demo")
    assert daten["letzter_schritt"] == 1
    assert daten["schritte"]["1"]["status"] == "ok"
    assert ist_halt("demo") is False
