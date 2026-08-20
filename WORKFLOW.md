# ablauf

zehn schritte. kein warten auf eine person.

seite zuerst, dann welten, dann welten an die orte auf der seite.

## schritte

1. **videos holen** — liste aus der kanal-url (`videos.json`)
2. **transkripte** — text je video unter `transcripts/<id>/text.txt`
3. **prüfung** — fertig oder offen (`pruefung.json`)
4. **bilder** — standbilder je video (`ffmpeg`)
5. **orte** — namen aus titel und text, lage wenn möglich (`orte.json`)
6. **wissen** — textstücke plus bilder (`wissen.json`)
7. **seite** — karte, orte, wissen, videos (3d-plätze noch leer)
8. **3d je ort**
   - blender-skript, glb bauen
   - prüfen (ray, `verify_ok.txt`)
   - **chisel:** glb hochladen, kamera setzen
   - **sicht live:** screenshot, bild lesen, bei abweichung kamera/prompt anpassen (bis 3 runden)
   - panorama prüfen (wieder shot + anpassen)
   - **erst dann** welt (marble), umschau-shots, nochmal lesen
   - ohne verify kein chisel. ohne passende sicht kein welt-ok
   - fehlt cdp: `skip_chisel.txt` / `skip_marble.txt`
9. **kontrolle** — `verify_ok.txt` plus welt-bilder (oder skip). bei erfolg:
   `seite/out/kontrolle.json` und `seite/out/QA_PASSED.txt` (automatisch)
10. **welten auf die seite** — 3d an den passenden ort, dann online (wrangler)
    oder lokal (`online.json`)

## halt

datei `.halt` im kanal-ordner oder `"halt": true` in `stand.json`.

## notizen

- blender **vor** chisel
- keine keys committen
- andere zwei repos bleiben getrennt
