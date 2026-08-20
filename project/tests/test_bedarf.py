from __future__ import annotations

from bedarf import fehlt, hart_fehlt, text_fuer_mensch


def test_beispiel_ohne_blender_ist_kein_muss():
    daten = {
        "python": True,
        "yt_dlp": False,
        "ffmpeg": False,
        "blender": False,
        "cdp": False,
        "wrangler": False,
        "chisel_skript": False,
        "beispiel": True,
    }
    luecken = fehlt(daten, beispiel=True, bis=10)
    assert hart_fehlt(luecken) is False


def test_seite_ohne_blender_ist_kein_muss():
    daten = {
        "python": True,
        "yt_dlp": True,
        "ffmpeg": True,
        "blender": False,
        "cdp": False,
        "wrangler": False,
        "chisel_skript": False,
        "beispiel": False,
    }
    luecken = fehlt(daten, beispiel=False, bis=7)
    assert hart_fehlt(luecken) is False
    daten = {
        "python": True,
        "yt_dlp": False,
        "ffmpeg": True,
        "blender": True,
        "cdp": True,
        "wrangler": True,
        "chisel_skript": True,
        "beispiel": False,
    }
    luecken = fehlt(daten, beispiel=False, bis=3)
    assert hart_fehlt(luecken) is True
    text = text_fuer_mensch(daten, luecken)
    assert "yt-dlp" in text
    assert "fehlt" in text
