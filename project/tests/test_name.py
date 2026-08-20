from __future__ import annotations

from kanal.name import kanal_name


def test_at_name():
    assert kanal_name("https://www.youtube.com/@BeispielKanal/videos") == "beispielkanal"


def test_channel_id():
    assert kanal_name("https://www.youtube.com/channel/UCabc123") == "ucabc123"


def test_leer_bricht():
    try:
        kanal_name("   ")
    except ValueError as err:
        assert "fehlt" in str(err)
    else:
        raise AssertionError("sollte fehlschlagen")
