"""werkzeuge prüfen, pip wenn möglich, mensch informieren."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bedarf import fehlt, hart_fehlt, status, text_fuer_mensch

REPO = ROOT.parent


def main(argv: list[str] | None = None) -> int:
    args = _args(argv)
    if args.beispiel:
        os.environ["CHANNEL_SITE_BEISPIEL"] = "1"
    if args.pip:
        _pip()
    daten = status(beispiel=args.beispiel)
    luecken = fehlt(daten, beispiel=args.beispiel, bis=args.bis)
    print(text_fuer_mensch(daten, luecken))
    if hart_fehlt(luecken):
        print("stop: ohne die muss-punkte geht dieser lauf nicht.")
        return 1
    return 0


def _pip() -> None:
    pyproject = REPO / "pyproject.toml"
    if not pyproject.is_file():
        raise RuntimeError("pyproject.toml fehlt")
    befehl = [sys.executable, "-m", "pip", "install", "-e", f"{REPO}[dev]"]
    fertig = subprocess.run(befehl)
    if fertig.returncode != 0:
        raise RuntimeError("pip install fehlgeschlagen")


def _args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="werkzeuge prüfen")
    parser.add_argument("--bis", type=int, default=10)
    parser.add_argument("--beispiel", action="store_true")
    parser.add_argument("--pip", action="store_true", help="pip install -e .[dev]")
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
