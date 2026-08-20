from __future__ import annotations

from welt.plan import ort_plan
from welt.pruefen import pruef_text
from welt.skript import skript_text


def test_skript_hat_export():
    plan = ort_plan({"slug": "forum", "oeffnungen": 2, "name": "Forum"})
    text = skript_text(plan)
    assert "EXPORT_OK" in text
    assert "gltf" in text
    assert "Boolean" not in text


def test_pruef_hat_verify():
    plan = ort_plan({"slug": "forum", "oeffnungen": 2, "name": "Forum"})
    text = pruef_text(plan)
    assert "VERIFY" in text
    assert "ray_cast" in text
    assert "forum.glb" in text
