from __future__ import annotations

from pathlib import Path

import pytest

from tests.png_bau import pad_png
from welt.chisel import MAX_RUNDEN, chisel_laufen


class FakeTreiber:
    def __init__(self, shots: list[Path]) -> None:
        self.shots = shots
        self.i = 0
        self.anpassungen: list[str] = []
        self.gestartet = False
        self.pano = None
        self.welt_url = "http://lokal/world"

    def start(self, glb: Path, prompt: str) -> None:
        self.gestartet = True

    def screenshot(self, pfad: Path) -> None:
        quelle = self.shots[min(self.i, len(self.shots) - 1)]
        pfad.write_bytes(quelle.read_bytes())
        self.i += 1

    def anpassen(self, aenderung: str, prompt: str) -> None:
        self.anpassungen.append(aenderung)

    def panorama(self, ordner: Path) -> Path:
        ziel = ordner / "pano_cdn.png"
        ziel.write_bytes(self.shots[-1].read_bytes())
        self.pano = ziel
        return ziel

    def welt(self) -> str:
        return self.welt_url

    def umschau(self, ordner: Path) -> None:
        for name in ("front", "right", "back", "left"):
            ziel = ordner / f"world_{name}.png"
            ziel.write_bytes(self.shots[-1].read_bytes())


def test_chisel_ohne_verify_bricht(tmp_path):
    (tmp_path / "x.glb").write_bytes(b"glb")
    with pytest.raises(RuntimeError, match="verify_ok"):
        chisel_laufen(tmp_path, "prompt")


def test_chisel_live_passt_an(tmp_path, monkeypatch):
    import config

    monkeypatch.setattr(config, "MIN_PANO_PX", 1)
    dunkel = tmp_path / "dunkel.png"
    hell = tmp_path / "hell.png"
    pad_png(dunkel, (0, 0, 0))
    pad_png(hell, (80, 80, 80), px=8)
    (tmp_path / "verify_ok.txt").write_text("VERIFY OK\n", encoding="utf-8")
    (tmp_path / "x.glb").write_bytes(b"glb")
    refs = tmp_path / "referenzen"
    refs.mkdir()
    pad_png(refs / "ref.png", (85, 85, 85))
    treiber = FakeTreiber([dunkel, hell])
    ergebnis = chisel_laufen(tmp_path, "prompt", treiber=treiber)
    assert treiber.gestartet is True
    assert "kamera_hoch" in treiber.anpassungen
    assert ergebnis["status"] == "ok"
    assert (tmp_path / "sicht.json").is_file()
    assert MAX_RUNDEN >= 2
