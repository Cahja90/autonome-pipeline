# ablauf

zehn schritte. kein warten auf eine person in der kontrolle.
ein echter kanal und das online-stellen brauchen trotzdem eine freigabe.

seite zuerst, dann welten, dann welten an die orte auf der seite.

stand: 12. november 2026.

## schritte

1. **videos holen** — liste aus der kanal-url (`videos.json`)
2. **transkripte** — text je video unter `transcripts/<id>/text.txt`, über yt-dlp. kein sprachmodell im beispiel
3. **prüfung** — fertig oder offen (`pruefung.json`)
4. **bilder** — standbilder je video (`ffmpeg`). im beispiel nur gemalt
5. **orte** — namen aus titel und text, lage wenn möglich (`orte.json`)
6. **wissen** — textstücke plus bilder (`wissen.json`). suche bleibt lokal im text
7. **seite** — karte, orte, wissen, videos (3d-plätze noch leer)
8. **3d je ort**
   - modell heute: `marble-1.1` (`CHANNEL_SITE_MARBLE_MODELL`, größer: `marble-1.1-plus`)
   - blender-skript, glb bauen
   - prüfen (ray, `verify_ok.txt`)
   - **chisel:** glb hochladen, kamera setzen. chisel ist der editor, kein api-name
   - **sicht live:** screenshot, bild lesen, bei abweichung kamera/prompt anpassen (bis 3 runden)
   - sicht-name heute: `claude-sonnet-5.5`, oder der befehl `CHANNEL_SITE_SICHT_CMD`
   - panorama prüfen (wieder shot + anpassen)
   - **erst dann** welt, umschau-shots, nochmal lesen
   - ohne verify kein chisel. ohne passende sicht kein welt-ok
   - fehlt cdp: `skip_chisel.txt` / `skip_marble.txt`
   - beispiel: keine echte welt, nur `sicht_beispiel.png`
9. **kontrolle** — `verify_ok.txt` plus welt-bilder (oder skip). bei erfolg:
   `seite/out/kontrolle.json` und `seite/out/QA_PASSED.txt`
10. **welten auf die seite** — 3d an den passenden ort, dann online (wrangler)
    oder lokal (`online.json`). beispiel bleibt lokal

## halt

datei `.halt` im kanal-ordner oder `"halt": true` in `stand.json`.

## notizen

- blender **vor** chisel
- keine keys, keine namen, keine mails ins repo
- andere zwei repos bleiben getrennt
- gemalte bilder sind keine belege für eine echte welt
