"""ray_cast gegen denselben grundriss. ohne ok kein marble."""

from __future__ import annotations

from pathlib import Path


def pruef_text(plan: dict) -> str:
    slug = plan["slug"]
    tuer_tests = []
    for tuer in plan["tueren"]:
        tuer_tests.append(
            f'_tuer("{tuer["name"]}", {tuer["x"]:.3f}, {plan["wand_y"]:.3f})'
        )
    block = plan["waende_block"][0]
    tuer_block = ",\n    ".join(tuer_tests)
    return f'''import os
import sys
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
GLB = os.path.join(HERE, "{slug}.glb")
if not os.path.isfile(GLB):
    print("MISSING", GLB)
    sys.exit(1)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=GLB)
sc = bpy.context.scene
dg = bpy.context.evaluated_depsgraph_get()


def ray(origin, direction, dist=60):
    o = Vector(origin)
    d = Vector(direction).normalized()
    hit, loc, nrm, idx, obj, mat = sc.ray_cast(dg, o, d, distance=dist)
    return hit, (obj.name if obj else None), (tuple(round(v, 2) for v in loc) if hit else None)


def _tuer(name, x, wand_y):
    hit, obj, loc = ray((x, wand_y - 6.0, 1.5), (0, 1, 0))
    blocked = hit and loc is not None and abs(loc[1] - wand_y) < 1.2
    return name + "_frei", not blocked, f"hit={{obj}}@{{loc}}"


tests = [
    {tuer_block},
]

hit, obj, loc = ray(({block["x"]:.3f}, {plan["wand_y"]:.3f} - 6.0, 1.5), (0, 1, 0))
tests.append(
    (
        "wand_haelt",
        bool(hit and loc is not None and abs(loc[1] - {plan["wand_y"]:.3f}) < 1.2),
        f"hit={{obj}}@{{loc}}",
    )
)

ok = True
for name, passed, info in tests:
    print(("PASS" if passed else "FAIL"), name, "|", info)
    ok = ok and passed
print("VERIFY", "OK" if ok else "FAILED")
sys.exit(0 if ok else 1)
'''


def pruef_schreiben(plan: dict, ordner: Path) -> Path:
    pfad = ordner / f"verify_{plan['slug']}.py"
    pfad.parent.mkdir(parents=True, exist_ok=True)
    pfad.write_text(pruef_text(plan), encoding="utf-8")
    return pfad
