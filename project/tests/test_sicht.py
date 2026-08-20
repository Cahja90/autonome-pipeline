from __future__ import annotations

from tests.png_bau import pad_png
from welt.sicht import png_helligkeit, sicht_pruefen


def test_dunkel_wird_kamera_hoch(tmp_path):
    shot = tmp_path / "sicht_live_1.png"
    pad_png(shot, (0, 0, 0))
    bericht = sicht_pruefen(shot, [])
    assert bericht["ok"] is False
    assert bericht["aenderung"] == "kamera_hoch"
    assert png_helligkeit(shot) < 12


def test_passt_zur_referenz(tmp_path):
    shot = tmp_path / "sicht_live_1.png"
    ref = tmp_path / "ref.png"
    pad_png(shot, (80, 80, 80))
    pad_png(ref, (90, 90, 90))
    bericht = sicht_pruefen(shot, [ref])
    assert bericht["ok"] is True
    assert bericht["aenderung"] == "ok"
