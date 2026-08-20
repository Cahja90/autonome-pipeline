# Agent setup (MUST)

You are setting up **this repo** so a human can run: YouTube channel URL → transcripts, stills, knowledge, 3D, static site.

**MUST NOT** `git push` (or `--force`) unless the human explicitly asked in this turn.

**MUST** write code like the owner: see user rule `code-regeln.mdc` + Clean Code Framework.

- identifiers: `snake_case` functions/vars, `PascalCase` types, `ALL_CAPS` constants, lowercase files
- comments: German, all lowercase, **no space after `#`** (`#fehlt blender` not `# fehlt blender`)
- user-facing text: short German everyday words (no hub/layer/center marketing)
- no silent `except:`
- tests first for new behavior

## First action (MUST)

```text
python project/einrichten.py --pip --beispiel
python project/einrichten.py --bis 10
```

(`--beispiel` = no network, for smoke. Live channel: omit `--beispiel`.)

Read stdout. That is the source of truth for what exists.

## Screenshot / image check (MUST)

**Before** step 8 (chisel / welt), you MUST verify that **this** agent can **see and judge screenshots** — not only file size.

Check all of:

1. You can open image files (`pano_*.png`, `sicht_live_*.png`, `world_*.png`, referenzen) and describe them.
2. You can compare a shot to the place referenzen (openings, silhouette, lighting, no black bars, no junk text).
3. You can decide `ok` / not ok and which live fix: `kamera_hoch`, `kamera_runter`, `prompt_oeffnungen`, `neu_shot`.
4. `welt/sicht.py` runs (`sicht_pruefen`). If `CHANNEL_SITE_SICHT_CMD` is set, that command must return JSON with `ok` and `aenderung`.

If you **cannot** read images (no vision, no `CHANNEL_SITE_SICHT_CMD`, tools fail):

- Tell the human in German: „bildprüfung geht nicht — diese KI kann screenshots nicht auswerten.“
- Do **not** mark welt/sicht as passed.
- Do **not** run Marble world as if the shots were checked.
- Stop that slice or skip with `skip_chisel.txt` and say why.

Pixel-only brightness in `sicht.py` is a **fallback**, not a replacement for reading the picture. If you have vision, **use it** on every live shot and world shot.

## If something is missing (MUST)

Tell the human in German, one bullet per gap, using the script output. Do not invent workarounds that skip gates.

| Missing | You may install | Human must do | Until then |
|---------|-----------------|---------------|------------|
| Python 3.11+ / pip | `pip install -e ".[dev]"` | install Python | stop |
| yt-dlp | `pip install yt-dlp` | — | no live channel fetch |
| ffmpeg | if package manager allowed; else ask | install ffmpeg | no live frames (step 4) |
| blender | **do not** silent-install GUI apps | install Blender 5.x, on PATH | no GLB/verify; **no chisel** |
| Chrome CDP port 9222 | — | start Chrome with `--remote-debugging-port=9222` and Marble login | skip chisel/world; write skip files |
| marble_chisel.py | set `CHANNEL_SITE_WORLD_ROOT` | sibling 3D repo | skip chisel |
| wrangler | `npm i -g wrangler` only if asked | Cloudflare login | site stays local (ok) |
| vision / screenshots | set `CHANNEL_SITE_SICHT_CMD` if you cannot see images yourself | human: use an agent that can read pictures | **no** screenshot QA; no welt-ok |

**MUST** say clearly: “3d-welt geht noch nicht, weil … fehlt.” Never claim the site has walkable worlds if chisel was skipped.

## Run order (MUST)

1. `einrichten.py` until no **muss**-gaps (or human accepts beispiel)
2. `python project/run.py --beispiel --bis 10` smoke
3. live: `python project/run.py --kanal "https://www.youtube.com/@…" --bis 10`
4. `python -m pytest`

Gates (do not reorder):

1. video list → 2. transcripts → 3. audit → 4. frames → 5. places → 6. knowledge
7. **site first** (map, places, knowledge, videos)
8. **then 3D per place:** Blender GLB + ray_cast `verify_ok.txt` BEFORE chisel. Screenshot loop reads images, adjusts camera/prompt live, **then** Marble world.
9. auto QA (`QA_PASSED.txt`)
10. **attach 3D worlds to the matching places on the site**, then deploy or keep local

No human in the loop for QA. If a tool is missing, skip that slice and **tell the human**.

## Env (never commit secrets)

- `CHANNEL_SITE_BEISPIEL=1` — demo data
- `CHANNEL_SITE_WORK` — work dir (default `project/work`)
- `CHANNEL_SITE_WORLD_ROOT` — existing 3D scripts
- `CHANNEL_SITE_SICHT_CMD` — optional vision command (JSON stdout: `ok`, `aenderung`)

## Halt

File `project/work/<kanal>/.halt` or `"halt": true` in `stand.json`.

## Conflicts

correctness & tests > conceptual integrity > changeability > simplicity.
