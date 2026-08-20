"""start: kanal-url, schritte 1 bis n."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bedarf import fehlt, hart_fehlt, status, text_fuer_mensch
from kanal.name import kanal_name
from schritte import NAMEN, bis_liste, schritt_ausfuehren
from stand import ist_halt, schritt_merken


def main(argv: list[str] | None = None) -> int:
    args = _args(argv)
    if args.beispiel:
        os.environ["CHANNEL_SITE_BEISPIEL"] = "1"
        kanal_url = "beispiel"
        kanal = "beispiel"
    else:
        kanal_url = args.kanal
        kanal = kanal_name(kanal_url)
    daten = status(beispiel=args.beispiel)
    luecken = fehlt(daten, beispiel=args.beispiel, bis=args.bis)
    print(text_fuer_mensch(daten, luecken))
    if args.check:
        return 1 if hart_fehlt(luecken) else 0
    if hart_fehlt(luecken):
        print("stop: richte die muss-punkte ein, dann nochmal starten.")
        return 3
    for nummer in bis_liste(args.bis):
        if ist_halt(kanal):
            print("halt")
            return 2
        print(f"{nummer} {NAMEN[nummer]} …")
        extra = schritt_ausfuehren(nummer, kanal_url, kanal)
        schritt_merken(kanal, nummer, "ok", extra)
        print(f"{nummer} {NAMEN[nummer]} ok")
    return 0


def _args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="kanal zur seite")
    parser.add_argument("--kanal", default="", help="youtube-url oder beispiel")
    parser.add_argument("--bis", type=int, default=10, help="letzter schritt 1-10")
    parser.add_argument("--beispiel", action="store_true", help="ohne netz")
    parser.add_argument("--check", action="store_true", help="nur werkzeuge zeigen")
    args = parser.parse_args(argv)
    if not args.beispiel and not args.kanal:
        parser.error("--kanal oder --beispiel")
    if args.kanal.strip() == "beispiel":
        args.beispiel = True
    return args


if __name__ == "__main__":
    raise SystemExit(main())
