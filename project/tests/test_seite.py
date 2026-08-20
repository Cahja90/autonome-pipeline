from __future__ import annotations

import struct
import zlib
from pathlib import Path

from ablage import json_schreiben
from kontrolle.bild import bild_ok
from kontrolle.pruefen import laufen as kontrolle_laufen
from seite.bauen import laufen


def test_seite_aus_orte(tmp_path, monkeypatch):
    import config

    monkeypatch.setattr(config, "WORK_DIR", tmp_path)
    kanal = "demo"
    wurzel = tmp_path / kanal
    json_schreiben(
        wurzel / "orte.json",
        [
            {
                "slug": "ostia",
                "name": "Ostia",
                "video_ids": ["abc123"],
                "oeffnungen": 2,
                "lat": 41.755,
                "lon": 12.291,
            },
            {
                "slug": "forum",
                "name": "Forum",
                "video_ids": ["xyz789"],
                "oeffnungen": 3,
                "lat": None,
                "lon": None,
            },
        ],
    )
    json_schreiben(
        wurzel / "wissen.json",
        {
            "chunks": [
                {
                    "video_id": "abc123",
                    "ort": "ostia",
                    "text": "hafenstadt am meer",
                    "bilder": [],
                }
            ]
        },
    )
    json_schreiben(
        wurzel / "videos.json",
        [
            {
                "video_id": "abc123",
                "title": "rundgang",
                "url": "https://www.youtube.com/watch?v=abc123",
            }
        ],
    )
    json_schreiben(wurzel / "stand.json", {"letzter_schritt": 7})
    ergebnis = laufen(kanal)
    ziel = Path(ergebnis["pfad"])
    index = ziel / "index.html"
    assert index.is_file()
    html = index.read_text(encoding="utf-8")
    assert "karte" in html
    assert "orte" in html
    assert "wissen aus videos" in html
    assert "ostia" in html.lower()
    assert 'id="suche"' in html
    assert "leaflet" in html
    ostia = (ziel / "ort" / "ostia.html").read_text(encoding="utf-8")
    assert "hafenstadt am meer" in ostia
    assert "youtube.com/watch?v=abc123" in ostia
    assert "41.755" in ostia
    forum = (ziel / "ort" / "forum.html").read_text(encoding="utf-8")
    assert "Forum" in forum
    assert "ohne koordinaten" in forum
    assert ergebnis["anzahl"] == 2
    #kontrolle ohne person: keine welt-ordner → tor offen
    qa = kontrolle_laufen(kanal)
    assert qa["ok"] is True
    assert (ziel / "out" / "QA_PASSED.txt").is_file()


def _png_bytes(breite: int, hoehe: int, extra: int = 0) -> bytes:
    def chunk(typ: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(typ + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + typ + data + struct.pack(">I", crc)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", breite, hoehe, 8, 2, 0, 0, 0)
    raw = b"".join(b"\x00" + b"\x00\x00\x00" * breite for _ in range(hoehe))
    body = (
        sig
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )
    if extra > 0:
        body += b"\x00" * extra
    return body


def test_bild_ok_rahmen(tmp_path):
    import config

    minst = config.MIN_FRAME_BYTES
    pfad = tmp_path / "frame_001.png"
    roh = _png_bytes(1, 1)
    extra = max(0, minst - len(roh))
    pfad.write_bytes(_png_bytes(1, 1, extra))
    gut, grund = bild_ok(pfad)
    assert gut is True, grund


def test_bild_ok_welt_braucht_pano_px(tmp_path):
    import config

    minst = config.MIN_FRAME_BYTES
    klein = tmp_path / "world_front.png"
    roh = _png_bytes(1, 1)
    klein.write_bytes(_png_bytes(1, 1, max(0, minst - len(roh))))
    gut, _grund = bild_ok(klein)
    assert gut is False
    gross = tmp_path / "world_back.png"
    roh = _png_bytes(config.MIN_PANO_PX, config.MIN_PANO_PX)
    extra = max(0, minst - len(roh))
    gross.write_bytes(
        _png_bytes(config.MIN_PANO_PX, config.MIN_PANO_PX, extra)
    )
    gut, grund = bild_ok(gross)
    assert gut is True, grund
