import os
import sys
from pathlib import Path

import flet as ft

from gui.app import TtsApp

# ── Point Flet to bundled Flutter engine (portable, no ~/.flet cache) ──
# Only active when the bundled directory exists (Nuitka build).
# In dev mode (python main.py), falls through to Flet's normal mechanism.
_EXE_DIR = Path(sys.argv[0]).resolve().parent
_FLET_VIEW = _EXE_DIR / "flet_client"
if sys.platform == "win32":
    _FLET_VIEW = _FLET_VIEW / "flet"
elif sys.platform == "linux":
    _FLET_VIEW = _FLET_VIEW / "flet"
# macOS: top-level .app is inside flet_client/

if (_FLET_VIEW / "flet.exe" if sys.platform == "win32" else _FLET_VIEW).exists() or _FLET_VIEW.exists():
    os.environ["FLET_VIEW_PATH"] = str(_FLET_VIEW)

if __name__ == "__main__":
    ft.run(main=TtsApp)
