# von der kanal-url zur seite

eine youtube-kanal-url wird zu transkripten, bildern, wissen, 3d und einer
seite mit karte. beliebiger youtube kanal (erlaubns nachfragen) .

die anderen zwei repos bleiben eigene projekte (transkripte, 3d-welten).
hier läuft die Pipeline bis zur seite.

## ablauf

1. videos vom kanal holen
2. transkripte holen
3. transkripte prüfen
4. bilder aus den videos
5. orte finden
6. wissen bauen
7. seite bauen (karte, orte, wissen, videos, 3d welt)
8. 3d welt je ort — blender prüfen, dann chisel. screenshots werden von der KI kontroliert und live angepasst (kamera/prompt), erst dann welt. ohne `verify_ok.txt`kein chisel.
9. kontrolle — KI schreibt `QA_PASSED.txt` selbst, wenn alles passt.
10. deploy der 3D welt zu den gehörigen  Orten auf der  RAG Internetseite.  



## start

zuerst werkzeuge (die KI macht das, du siehst was fehlt):

```powershell
python project/einrichten.py --pip --beispiel
python project/run.py --check --bis 10
```

fehlt etwas **muss**, sagt das skript stop und nennt den punkt.

dann:

```powershell
python project/run.py --beispiel --bis 10
```

beliebige kanal-url:

```powershell
python project/run.py --kanal "https://www.youtube.com/@Kanal" --bis 10
```

prüfen:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

für schritt 7: blender **vor** chisel. chisel macht shots, liest sie, passt live an.
ohne `verify_ok.txt` kein chisel. welt erst nach passender ansicht.
für schritt 10: wenn `wrangler` da ist, geht die seite online.

## stand

anleitung für die KI, die das einrichtet: [AGENTS.md](AGENTS.md)


## lizenz

MIT — siehe [LICENSE](LICENSE)
