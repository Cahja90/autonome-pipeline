from __future__ import annotations

from schritte import NAMEN, schritt_ausfuehren


def test_reihenfolge_seite_vor_welt():
    assert NAMEN[7] == "seite"
    assert NAMEN[8] == "welt"
    assert NAMEN[10] == "online"
