"""kanal-url zu ordnernamen."""

from __future__ import annotations

import re
from urllib.parse import urlparse


def kanal_name(kanal_url: str) -> str:
    text = (kanal_url or "").strip()
    if not text:
        raise ValueError("kanal-url fehlt")
    pfad = (urlparse(text).path or text).strip("/")
    treffer = re.search(r"@([^/\s]+)", text)
    if treffer:
        return _sauber(treffer.group(1))
    teile = [p for p in pfad.split("/") if p]
    if "channel" in teile:
        idx = teile.index("channel")
        if idx + 1 < len(teile):
            return _sauber(teile[idx + 1])
    if teile:
        return _sauber(teile[-1])
    raise ValueError("kanal-url nicht lesbar")


def _sauber(roh: str) -> str:
    name = re.sub(r"[^a-zA-Z0-9_-]+", "-", roh).strip("-").lower()
    if not name:
        raise ValueError("kanal-name leer")
    return name[:80]
