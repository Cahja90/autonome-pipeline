"""schritt 7: statische seite mit karte. 3d kommt in schritt 10 dazu."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from ablage import json_lesen, json_liste, json_schreiben
from config import kanal_ordner
from stand import schritt_merken

_BILD_ENDUNGEN = {".png", ".jpg", ".jpeg"}
_LEAFLET_CSS = (
    "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
)
_LEAFLET_JS = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
_MODEL_JS = (
    "https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"
)


def laufen(kanal: str) -> dict:
    wurzel = kanal_ordner(kanal)
    orte = json_liste(wurzel / "orte.json")
    wissen = json_lesen(wurzel / "wissen.json", {"chunks": []})
    chunks = wissen.get("chunks") or [] if isinstance(wissen, dict) else []
    videos = {v.get("video_id"): v for v in json_liste(wurzel / "videos.json")}
    stand = json_lesen(wurzel / "stand.json", {})
    ziel = wurzel / "seite"
    if ziel.exists():
        shutil.rmtree(ziel)
    (ziel / "ort").mkdir(parents=True)
    (ziel / "bilder").mkdir(parents=True)
    (ziel / "modelle").mkdir(parents=True)
    karten = _karten_daten(orte)
    liste_html = _liste_html(orte)
    (ziel / "index.html").write_text(
        _index_html(karten, liste_html),
        encoding="utf-8",
    )
    for ort in orte:
        _ort_seite(wurzel, ziel, ort, chunks, videos)
    json_schreiben(ziel / "orte.json", karten)
    schritt_merken(kanal, 7, "ok", {"anzahl": len(orte)})
    return {
        "anzahl": len(orte),
        "pfad": str(ziel),
        "letzter_schritt": stand.get("letzter_schritt"),
    }


def _karten_daten(orte: list) -> list:
    daten = []
    for ort in orte:
        daten.append(
            {
                "slug": ort.get("slug") or "",
                "name": ort.get("name") or ort.get("slug") or "ort",
                "lat": ort.get("lat"),
                "lon": ort.get("lon"),
            }
        )
    return daten


def _liste_html(orte: list) -> str:
    if not orte:
        return '<p class="leer">keine orte</p>'
    teile = ['<ul class="orte">']
    for ort in orte:
        slug = _esc(ort.get("slug") or "ort")
        name = _esc(ort.get("name") or slug)
        punkt = _hat_punkt(ort)
        wo = _koords(ort) if punkt else "ohne koordinaten"
        teile.append(
            "<li data-ort=\"{slug}\" data-name=\"{name}\">"
            '<a href="ort/{slug}.html">{name}</a>'
            '<span class="meta">{wo}</span></li>'.format(
                slug=slug, name=name, wo=_esc(wo)
            )
        )
    teile.append("</ul>")
    return "\n".join(teile)


def _ort_seite(
    wurzel: Path,
    ziel: Path,
    ort: dict,
    chunks: list,
    videos: dict,
) -> None:
    slug = str(ort.get("slug") or "ort")
    name = ort.get("name") or slug
    bild_pfade = _bilder_sammeln(wurzel, ort, chunks)
    bild_html = _bilder_html(ziel, slug, bild_pfade)
    snippets = _snippets(ort, chunks)
    video_html = _video_html(ort, videos)
    drei_d = _drei_d_html(wurzel, ziel, slug)
    koords = _koords(ort) if _hat_punkt(ort) else "ohne koordinaten"
    html = _ort_html(
        name=name,
        koords=koords,
        bild_html=bild_html,
        snippet_html=_snippet_html(snippets),
        video_html=video_html,
        drei_d_html=drei_d,
    )
    (ziel / "ort" / f"{slug}.html").write_text(html, encoding="utf-8")


def _bilder_sammeln(wurzel: Path, ort: dict, chunks: list) -> list[Path]:
    slug = ort.get("slug")
    treffer: list[Path] = []
    welt = wurzel / "welt" / str(slug)
    if welt.is_dir():
        for pfad in sorted(welt.iterdir()):
            if pfad.suffix.lower() in _BILD_ENDUNGEN:
                treffer.append(pfad)
    vids = set(ort.get("video_ids") or [])
    for chunk in chunks:
        if chunk.get("ort") not in {slug, ort.get("name")}:
            continue
        for roh in chunk.get("bilder") or []:
            pfad = Path(roh)
            if not pfad.is_file():
                pfad = wurzel / roh
            if pfad.is_file():
                treffer.append(pfad)
    for video_id in vids:
        ordner = wurzel / "bilder" / str(video_id)
        if not ordner.is_dir():
            continue
        for pfad in sorted(ordner.iterdir()):
            if pfad.suffix.lower() in _BILD_ENDUNGEN:
                treffer.append(pfad)
    gesehen: set[Path] = set()
    unique: list[Path] = []
    for pfad in treffer:
        key = pfad.resolve()
        if key in gesehen:
            continue
        gesehen.add(key)
        unique.append(pfad)
    return unique


def _bilder_html(ziel: Path, slug: str, pfade: list[Path]) -> str:
    if not pfade:
        return ""
    ordner = ziel / "bilder" / slug
    ordner.mkdir(parents=True, exist_ok=True)
    teile = ['<section><h2>bilder</h2><div class="galerie">']
    for i, quelle in enumerate(pfade, start=1):
        name = f"{i:03d}_{quelle.name}"
        shutil.copy2(quelle, ordner / name)
        teile.append(
            f'<img src="../bilder/{_esc(slug)}/{_esc(name)}" alt="{_esc(slug)}">'
        )
    teile.append("</div></section>")
    return "\n".join(teile)


def _snippets(ort: dict, chunks: list) -> list[str]:
    slug = ort.get("slug")
    name = ort.get("name")
    vids = set(ort.get("video_ids") or [])
    direkt = [
        c for c in chunks if c.get("ort") in {slug, name}
    ]
    if not direkt:
        direkt = [c for c in chunks if c.get("video_id") in vids]
    texte = []
    for chunk in direkt:
        text = (chunk.get("text") or "").strip()
        if not text:
            continue
        texte.append(text[:500])
        if len(texte) >= 8:
            break
    return texte


def _snippet_html(texte: list[str]) -> str:
    if not texte:
        return ""
    teile = ['<section><h2>wissen aus videos</h2>']
    for text in texte:
        teile.append(f"<blockquote>{_esc(text)}</blockquote>")
    teile.append("</section>")
    return "\n".join(teile)


def _video_html(ort: dict, videos: dict) -> str:
    ids = ort.get("video_ids") or []
    if not ids:
        return ""
    teile = ['<section><h2>videos</h2><ul>']
    for video_id in ids:
        eintrag = videos.get(video_id) or {}
        url = eintrag.get("url") or (
            f"https://www.youtube.com/watch?v={video_id}"
        )
        titel = eintrag.get("title") or video_id
        teile.append(
            f'<li><a href="{_esc(url)}">{_esc(titel)}</a></li>'
        )
    teile.append("</ul></section>")
    return "\n".join(teile)


def _drei_d_html(wurzel: Path, ziel: Path, slug: str) -> str:
    welt = wurzel / "welt" / slug
    glb = welt / f"{slug}.glb"
    if not glb.is_file() and welt.is_dir():
        andere = sorted(welt.glob("*.glb"))
        glb = andere[0] if andere else glb
    teile = []
    if glb.is_file():
        ziel_glb = ziel / "modelle" / f"{slug}.glb"
        shutil.copy2(glb, ziel_glb)
        teile.append(
            "<section><h2>3d-ansicht</h2>"
            f'<script type="module" src="{_MODEL_JS}"></script>'
            f'<model-viewer src="../modelle/{_esc(slug)}.glb" '
            'camera-controls touch-action="pan-y" '
            f'alt="{_esc(slug)}"></model-viewer></section>'
        )
    viewer = welt / "viewer.html"
    if viewer.is_file():
        kopie = ziel / "ort" / f"{slug}_viewer.html"
        shutil.copy2(viewer, kopie)
        teile.append(
            f'<p><a href="{_esc(slug)}_viewer.html">3d im viewer</a></p>'
        )
    return "\n".join(teile)


def _hat_punkt(ort: dict) -> bool:
    return ort.get("lat") is not None and ort.get("lon") is not None


def _koords(ort: dict) -> str:
    return f"{ort.get('lat')}, {ort.get('lon')}"


def _esc(wert) -> str:
    text = "" if wert is None else str(wert)
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _index_html(karten: list, liste_html: str) -> str:
    orte_json = json.dumps(karten, ensure_ascii=False).replace("<", "\\u003c")
    return f"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>orte</title>
  <link rel="stylesheet" href="{_LEAFLET_CSS}">
  <style>
{_css()}
  </style>
</head>
<body>
  <header>
    <p class="kicker">wissen aus videos</p>
    <h1>orte</h1>
  </header>
  <section>
    <h2>karte</h2>
    <div id="karte"></div>
  </section>
  <section>
    <h2>suche</h2>
    <label for="suche">orte filtern</label>
    <input id="suche" type="search" placeholder="name oder ort">
    {liste_html}
  </section>
  <script src="{_LEAFLET_JS}"></script>
  <script>
const ORTE = {orte_json};
{_index_js()}
  </script>
</body>
</html>
"""


def _ort_html(
    name: str,
    koords: str,
    bild_html: str,
    snippet_html: str,
    video_html: str,
    drei_d_html: str,
) -> str:
    return f"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{_esc(name)}</title>
  <style>
{_css()}
model-viewer {{ width: 100%; height: 360px; }}
  </style>
</head>
<body>
  <header>
    <p><a href="../index.html">zurück zu den orten</a></p>
    <h1>{_esc(name)}</h1>
    <p class="meta">{_esc(koords)}</p>
  </header>
  {bild_html}
  {snippet_html}
  {video_html}
  {drei_d_html}
</body>
</html>
"""


def _css() -> str:
    return """body {
  margin: 0 auto; max-width: 960px; padding: 1.2rem;
  font-family: Georgia, "Times New Roman", serif;
  color: #1a1a1a; background: #fafafa; line-height: 1.45;
}
h1, h2 { font-weight: normal; }
.kicker { letter-spacing: 0.04em; color: #555; margin-bottom: 0; }
.meta { color: #555; font-size: 0.95rem; }
#karte { height: 420px; border: 1px solid #ddd; margin: 0.5rem 0 1.2rem; }
label { display: block; margin-bottom: 0.3rem; }
#suche { width: 100%; max-width: 28rem; padding: 0.4rem 0.5rem; }
.orte { list-style: none; padding: 0; }
.orte li { padding: 0.45rem 0; border-bottom: 1px solid #eee; }
.orte .meta { margin-left: 0.6rem; }
.galerie { display: flex; flex-wrap: wrap; gap: 0.6rem; }
.galerie img { max-width: 280px; height: auto; border: 1px solid #ddd; }
blockquote { margin: 0 0 1rem; padding: 0.6rem 0.8rem; background: #fff;
  border-left: 3px solid #ccc; }
.leer { color: #555; }
a { color: #1a1a1a; }
"""


def _index_js() -> str:
    return """
function html_text(wert) {
  return String(wert)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function karte_bauen(orte) {
  var karte = L.map("karte");
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap"
  }).addTo(karte);
  var punkte = [];
  orte.forEach(function (ort) {
    if (ort.lat === null || ort.lon === null) {
      return;
    }
    if (ort.lat === undefined || ort.lon === undefined) {
      return;
    }
    var marker = L.marker([ort.lat, ort.lon]).addTo(karte);
    marker.bindPopup(
      '<a href="ort/' + encodeURIComponent(ort.slug) + '.html">' +
      html_text(ort.name) + "</a>"
    );
    punkte.push([ort.lat, ort.lon]);
  });
  if (punkte.length === 1) {
    karte.setView(punkte[0], 10);
  } else if (punkte.length > 1) {
    karte.fitBounds(punkte, { padding: [24, 24] });
  } else {
    karte.setView([20, 0], 2);
  }
}

function liste_filtern() {
  var frage = (document.getElementById("suche").value || "").toLowerCase();
  document.querySelectorAll("[data-ort]").forEach(function (zeile) {
    var name = (zeile.getAttribute("data-name") || "").toLowerCase();
    var slug = (zeile.getAttribute("data-ort") || "").toLowerCase();
    var treffer = !frage || name.indexOf(frage) !== -1 ||
      slug.indexOf(frage) !== -1;
    zeile.hidden = !treffer;
  });
}

karte_bauen(ORTE);
document.getElementById("suche").addEventListener("input", liste_filtern);
"""
