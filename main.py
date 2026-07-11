import os
import sys
from pathlib import Path

import flet as ft

from gui.app import TtsApp

# ── Point Flet to bundled Flutter engine (portable, no ~/.flet cache) ──
# Only active when the bundled directory exists (Nuitka build).
# In dev mode (python main.py), falls through to Flet's normal mechanism.
_EXE_DIR = Path(sys.argv[0]).resolve().parent
if sys.platform == "darwin":
    # main.app/Contents/MacOS → ../../.. → Flet.app alongside main.app
    _FLET_VIEW = _EXE_DIR.parent.parent.parent / "Flet.app"
elif sys.platform == "win32":
    _FLET_VIEW = _EXE_DIR / "flet_client" / "flet"
else:
    _FLET_VIEW = _EXE_DIR / "flet_client" / "flet"

if _FLET_VIEW.exists():
    os.environ["FLET_VIEW_PATH"] = str(_FLET_VIEW)

if __name__ == "__main__":
    ft.run(main=TtsApp)
