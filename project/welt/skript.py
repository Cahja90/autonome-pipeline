"""blender-skript wie ostia: waende mit luecken, kein boolean."""

from __future__ import annotations

from pathlib import Path

from welt.plan import HALBE_BREITE, TUER_HOEHE, WAND_TIEFE, WAND_Y, WAND_Z


def skript_text(plan: dict) -> str:
    tueren = plan["tueren"]
    teile = _wand_teile(tueren)
    teile_src = ",\n    ".join(
        f"({a:.3f}, {b:.3f})" for a, b in teile
    )
    lintel = ",\n    ".join(
        f"({t['x']:.3f}, {t['breite']:.3f})" for t in tueren
    )
    slug = plan["slug"]
    return f'''import bpy
import math
import os

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene


def mat(name, rgb, rough=0.9):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*rgb, 1)
    bsdf.inputs["Roughness"].default_value = rough
    return m


BRICK = mat("brick", (0.55, 0.25, 0.16))
TUFA = mat("tufa", (0.72, 0.66, 0.55))
EARTH = mat("earth", (0.45, 0.38, 0.28))


def box(name, loc, scale, material):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = (scale[0] / 2, scale[1] / 2, scale[2] / 2)
    bpy.ops.object.transform_apply(scale=True)
    if material:
        o.data.materials.append(material)
    return o


box("ground", (0, 0, -0.5), (80, 80, 1), EARTH)

Y = {WAND_Y}
Z = {WAND_Z}
D = {WAND_TIEFE}
H_DOOR = {TUER_HOEHE}

teile = [
    {teile_src}
]
for i, (a, b) in enumerate(teile):
    w = b - a
    if w < 0.2:
        continue
    x = (a + b) / 2
    box(f"wand_{{i}}", (x, Y, Z / 2), (w, D, Z), BRICK)

lintels = [
    {lintel}
]
for i, (x, br) in enumerate(lintels):
    rest = Z - H_DOOR
    box(
        f"sturz_{{i}}",
        (x, Y, H_DOOR + rest / 2),
        (br, D, rest),
        BRICK,
    )

box("wand_s", (0, -Y, Z / 2), ({HALBE_BREITE} * 2, D, Z), BRICK)
box("wand_w", (-{HALBE_BREITE}, 0, Z / 2), (D, {WAND_Y} * 2, Z), BRICK)
box("wand_o", ({HALBE_BREITE}, 0, Z / 2), (D, {WAND_Y} * 2, Z), BRICK)

sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
sun.data.energy = 4
sun.rotation_euler = (math.radians(50), 0, math.radians(30))
sc.collection.objects.link(sun)

outdir = os.path.dirname(os.path.abspath(__file__))
bpy.ops.export_scene.gltf(
    filepath=os.path.join(outdir, "{slug}.glb"),
    export_format="GLB",
)
print("EXPORT_OK")
'''


def _wand_teile(tueren: list[dict]) -> list[tuple[float, float]]:
    kanten = [-HALBE_BREITE]
    for tuer in sorted(tueren, key=lambda t: t["x"]):
        halb = tuer["breite"] / 2
        kanten.append(tuer["x"] - halb)
        kanten.append(tuer["x"] + halb)
    kanten.append(HALBE_BREITE)
    teile = []
    for i in range(0, len(kanten) - 1, 2):
        teile.append((kanten[i], kanten[i + 1]))
    return teile


def skript_schreiben(plan: dict, ordner: Path) -> Path:
    pfad = ordner / f"build_{plan['slug']}.py"
    pfad.parent.mkdir(parents=True, exist_ok=True)
    pfad.write_text(skript_text(plan), encoding="utf-8")
    return pfad
