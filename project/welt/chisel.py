"""chisel live: shot, lesen, anpassen, erst dann welt."""

from __future__ import annotations

import sys
from pathlib import Path

from ablage import json_schreiben
from config import WORLD_ROOT
from welt.marmor import _chrome_port_frei, _skip
from welt.sicht import sicht_pruefen

MAX_RUNDEN = 3
BILD_ENDUNGEN = {".png", ".jpg", ".jpeg"}


def chisel_laufen(
    ort_ordner: Path,
    prompt: str,
    treiber=None,
) -> dict:
    if not (ort_ordner / "verify_ok.txt").is_file():
        raise RuntimeError("kein verify_ok.txt — chisel verboten")
    glb = _glb(ort_ordner)
    if glb is None:
        raise RuntimeError("kein glb")
    if treiber is None:
        treiber = echter_treiber()
    if treiber is None:
        _skip(ort_ordner, "chisel/cdp fehlt")
        (ort_ordner / "skip_chisel.txt").write_text("cdp fehlt\n", encoding="utf-8")
        return {"status": "skip", "grund": "cdp fehlt"}
    refs = _refs(ort_ordner)
    treiber.start(glb, prompt)
    live = _live_shots(treiber, ort_ordner, refs, prompt)
    if not live["ok"]:
        json_schreiben(ort_ordner / "sicht.json", live)
        _skip(ort_ordner, "sicht live nicht ok")
        return {"status": "sicht_fail", "sicht": live}
    pano = treiber.panorama(ort_ordner)
    pano_bericht = _pano_pruefen(treiber, ort_ordner, pano, refs, prompt)
    live["pano"] = pano_bericht
    if not pano_bericht.get("ok"):
        json_schreiben(ort_ordner / "sicht.json", live)
        _skip(ort_ordner, "pano nicht ok")
        return {"status": "pano_fail", "sicht": live}
    url = treiber.welt()
    treiber.umschau(ort_ordner)
    welt_berichte = _welt_pruefen(ort_ordner, refs)
    live["welt"] = welt_berichte
    live["ok"] = all(b.get("ok") for b in welt_berichte) if welt_berichte else True
    live["url"] = url
    json_schreiben(ort_ordner / "sicht.json", live)
    if not live["ok"]:
        _skip(ort_ordner, "welt-shots nicht ok")
        return {"status": "welt_sicht_fail", "sicht": live}
    return {"status": "ok", "sicht": live, "url": url}


def echter_treiber():
    if not _chrome_port_frei():
        return None
    skript_ordner = WORLD_ROOT / "scripts"
    if not (skript_ordner / "marble_chisel.py").is_file():
        return None
    pfad = str(skript_ordner)
    if pfad not in sys.path:
        sys.path.insert(0, pfad)
    from marble_chisel import MarbleChisel

    return CdpTreiber(MarbleChisel())


class CdpTreiber:
    def __init__(self, chisel) -> None:
        self.chisel = chisel
        self.prompt = ""

    def start(self, glb: Path, prompt: str) -> None:
        self.prompt = prompt
        self.chisel.open_chisel()
        self.chisel.close_tos()
        self.chisel.upload_glb(str(glb))
        self.chisel.set_prompt(prompt)
        self.chisel.place_pano_camera()

    def screenshot(self, pfad: Path) -> None:
        pfad.parent.mkdir(parents=True, exist_ok=True)
        self.chisel.m.screenshot(str(pfad))

    def anpassen(self, aenderung: str, prompt: str) -> None:
        if aenderung == "kamera_runter":
            self.chisel.place_pano_camera()
            return
        if aenderung == "kamera_hoch":
            _kamera_hoch(self.chisel)
            return
        if aenderung == "prompt_oeffnungen":
            extra = prompt + " Preserve every opening. Match reference silhouette."
            self.chisel.set_prompt(extra)
            self.prompt = extra

    def panorama(self, ordner: Path) -> Path | None:
        pano = self.chisel.generate_panorama(str(ordner))
        if not pano:
            return None
        return Path(pano)

    def welt(self) -> str:
        return self.chisel.create_world()

    def umschau(self, ordner: Path) -> None:
        self.chisel.orbit_shots(str(ordner), prefix="world")


def _live_shots(treiber, ordner: Path, refs: list[Path], prompt: str) -> dict:
    runden = []
    ok = False
    for i in range(1, MAX_RUNDEN + 1):
        shot = ordner / f"sicht_live_{i}.png"
        treiber.screenshot(shot)
        bericht = sicht_pruefen(shot, refs)
        bericht["runde"] = i
        runden.append(bericht)
        if bericht["ok"]:
            ok = True
            break
        treiber.anpassen(bericht["aenderung"], prompt)
    return {"ok": ok, "runden": runden}


def _pano_pruefen(treiber, ordner: Path, pano: Path | None, refs: list[Path], prompt: str) -> dict:
    if pano is None or not pano.is_file():
        return {"ok": False, "grund": "pano fehlt", "aenderung": "neu_shot"}
    bericht = sicht_pruefen(pano, refs)
    if bericht["ok"]:
        return bericht
    for i in range(1, MAX_RUNDEN):
        treiber.anpassen(bericht["aenderung"], prompt)
        neu = treiber.panorama(ordner)
        if neu is None:
            break
        bericht = sicht_pruefen(neu, refs)
        bericht["runde"] = i + 1
        if bericht["ok"]:
            return bericht
    return bericht


def _welt_pruefen(ordner: Path, refs: list[Path]) -> list[dict]:
    berichte = []
    for pfad in sorted(ordner.iterdir()):
        name = pfad.name.lower()
        if pfad.suffix.lower() not in BILD_ENDUNGEN:
            continue
        if not name.startswith("world_"):
            continue
        berichte.append(sicht_pruefen(pfad, refs))
    return berichte


def _glb(ordner: Path) -> Path | None:
    treffer = sorted(ordner.glob("*.glb"))
    if not treffer:
        return None
    return treffer[0]


def _refs(ordner: Path) -> list[Path]:
    refs = ordner / "referenzen"
    if not refs.is_dir():
        return []
    return [p for p in sorted(refs.iterdir()) if p.suffix.lower() in BILD_ENDUNGEN]


def _kamera_hoch(chisel) -> None:
    vp = chisel.m.eval(
        "(()=>{const c=[...document.querySelectorAll('canvas')];"
        "if(!c.length)return null;"
        "const r=c[0].getBoundingClientRect();"
        "return {cx:r.left+r.width/2, cy:r.top+r.height/2, h:r.height};})()"
    )
    if not vp:
        return
    x0, y0 = vp["cx"], vp["cy"]
    y1 = y0 - vp["h"] * 0.28
    chisel.m.cmd(
        "Input.dispatchMouseEvent",
        {"type": "mousePressed", "x": x0, "y": y0, "button": "left", "clickCount": 1},
    )
    for i in range(1, 13):
        y = y0 + (y1 - y0) * i / 12
        chisel.m.cmd(
            "Input.dispatchMouseEvent",
            {"type": "mouseMoved", "x": x0, "y": y, "button": "left"},
        )
    chisel.m.cmd(
        "Input.dispatchMouseEvent",
        {"type": "mouseReleased", "x": x0, "y": y1, "button": "left", "clickCount": 1},
    )
