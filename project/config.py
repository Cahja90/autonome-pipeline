"""pfade und umgebung. keine secrets im repo."""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
ROOT_DIR = PROJECT_DIR.parent
WORK_DIR = Path(os.environ.get("CHANNEL_SITE_WORK", PROJECT_DIR / "work"))

TRANSCRIPT_ROOT = Path(
    os.environ.get(
        "CHANNEL_SITE_TRANSCRIPT_ROOT",
        ROOT_DIR.parent / "publish" / "antike-transcript-pipeline" / "project",
    )
)
WORLD_ROOT = Path(
    os.environ.get(
        "CHANNEL_SITE_WORLD_ROOT",
        ROOT_DIR.parent / "publish" / "antike-3d-world-pipeline" / "project" / "pipeline",
    )
)

STEP_MAX = 10
DEFAULT_FPS_EVERY = 5
MIN_FRAME_BYTES = 8_000
MIN_PANO_PX = 400
BLACK_MEAN_MAX = 12.0
WHITE_MEAN_MIN = 243.0

#namen von heute. austauschbar, kein key, kein aufruf im beispiel
MARBLE_MODELL = (
    os.environ.get("CHANNEL_SITE_MARBLE_MODELL", "marble-1.1").strip() or "marble-1.1"
)
SICHT_MODELL = (
    os.environ.get("CHANNEL_SITE_SICHT_MODELL", "claude-sonnet-5.5").strip()
    or "claude-sonnet-5.5"
)
SUCHE_ART = "lokal"


def kanal_ordner(kanal: str) -> Path:
    return WORK_DIR / kanal
