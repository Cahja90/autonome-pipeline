from __future__ import annotations

from pathlib import Path

import pytest

from welt.marmor import marble_starten


def test_marble_ohne_verify_bricht(tmp_path):
    (tmp_path / "x.glb").write_bytes(b"glb")
    with pytest.raises(RuntimeError, match="verify_ok"):
        marble_starten(tmp_path, "prompt")
