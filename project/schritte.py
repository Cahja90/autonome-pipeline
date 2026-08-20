"""zehn schritte nacheinander."""

from __future__ import annotations

from bilder.holen import laufen as bilder_laufen
from kanal.liste import laufen as liste_laufen
from kanal.pruefung import laufen as pruefung_laufen
from kanal.transkript import laufen as transkript_laufen
from kontrolle.pruefen import laufen as kontrolle_laufen
from online.stellen import laufen as online_laufen
from orte.finden import laufen as orte_laufen
from seite.bauen import laufen as seite_laufen
from welt.laufen import laufen as welt_laufen
from wissen.index import laufen as wissen_laufen

NAMEN = {
    1: "liste",
    2: "transkripte",
    3: "pruefung",
    4: "bilder",
    5: "orte",
    6: "wissen",
    7: "seite",
    8: "welt",
    9: "kontrolle",
    10: "online",
}


def bis_liste(bis: int) -> list[int]:
    if bis < 1 or bis > 10:
        raise ValueError("bis muss 1 bis 10 sein")
    return list(range(1, bis + 1))


def schritt_ausfuehren(nummer: int, kanal_url: str, kanal: str) -> dict:
    if nummer == 1:
        return liste_laufen(kanal_url, kanal)
    if nummer == 2:
        return transkript_laufen(kanal)
    if nummer == 3:
        return pruefung_laufen(kanal)
    if nummer == 4:
        return bilder_laufen(kanal)
    if nummer == 5:
        return orte_laufen(kanal)
    if nummer == 6:
        return wissen_laufen(kanal)
    if nummer == 7:
        return seite_laufen(kanal)
    if nummer == 8:
        return welt_laufen(kanal)
    if nummer == 9:
        return kontrolle_laufen(kanal)
    if nummer == 10:
        return online_laufen(kanal)
    raise ValueError(f"unbekannter schritt {nummer}")
