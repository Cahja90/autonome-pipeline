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


def kanal_ordner(kanal: str) -> Path:
    return WORK_DIR / kanal
