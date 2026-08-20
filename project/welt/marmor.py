"""marble nur nach verify. sonst halt."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from config import WORLD_ROOT


def marble_starten(ort_ordner: Path, prompt: str) -> str:
    glb = list(ort_ordner.glob("*.glb"))
    if not (ort_ordner / "verify_ok.txt").is_file():
        raise RuntimeError("kein verify_ok.txt — marble verboten")
    if not glb:
        raise RuntimeError("kein glb")
    skript = WORLD_ROOT / "scripts" / "marble_chisel.py"
    if not skript.is_file():
        _skip(ort_ordner, "marble-skript fehlt")
        return "skip"
    if not _chrome_port_frei():
        _skip(ort_ordner, "cdp port 9222 zu")
        return "skip"
    befehl = [
        os.environ.get("PYTHON", "python"),
        str(skript),
        str(ort_ordner),
        prompt,
        "--world",
    ]
    fertig = subprocess.run(befehl, capture_output=True, text=True)
    if fertig.returncode != 0:
        extra = (fertig.stderr or fertig.stdout or "").strip()
        _skip(ort_ordner, extra or "marble fehlgeschlagen")
        return "skip"
    return "ok"


def _skip(ordner: Path, grund: str) -> None:
    (ordner / "skip_marble.txt").write_text(grund + "\n", encoding="utf-8")


def _chrome_port_frei() -> bool:
    #cdp standard 9222, nur grober check
    try:
        import socket

        sock = socket.create_connection(("127.0.0.1", 9222), timeout=0.3)
        sock.close()
        return True
    except OSError:
        return False
