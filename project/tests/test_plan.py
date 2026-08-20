from __future__ import annotations

from welt.plan import ort_plan


def test_plan_hat_tueren():
    plan = ort_plan({"slug": "forum", "oeffnungen": 3, "name": "Forum"})
    assert plan["slug"] == "forum"
    assert len(plan["tueren"]) == 3
    assert len(plan["waende_block"]) >= 1
    for tuer in plan["tueren"]:
        assert "x" in tuer
        assert tuer["breite"] > 0
