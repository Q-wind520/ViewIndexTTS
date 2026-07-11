"""Nuitka build script for ATRI-IndexTTS-GUI.

Usage:
    python build.py               # dev build (standalone folder)
    python build.py --onefile     # single exe (slower, easier to distribute)
"""

import subprocess
import sys
import urllib.request
from pathlib import Path

import flet_desktop
import flet_desktop.version

NUITKA_ARGS = [
    sys.executable, "-m", "nuitka",
    "--standalone",
    "--enable-plugin=tk-inter",
    "--include-package=gui,httpx,playsound3,dotenv,flet,flet_desktop",
    "--include-package-data=flet,flet_desktop",
    "--include-data-dir=gui=gui",
    "--output-dir=dist",
    "--output-filename=ATRI-IndexTTS",
    "--assume-yes-for-downloads",
]

FLET_ARTIFACTS: dict[str, str] = {
    "win32": "flet-windows.zip",
    "darwin": "flet-macos.tar.gz",
    "linux": "flet-linux-ubuntu24.04-amd64.tar.gz",
}


def _ensure_flet_client() -> None:
    """Download Flet desktop runtime to flet_desktop/app/ so Nuitka can bundle it."""
    artifact = FLET_ARTIFACTS.get(sys.platform)
    if artifact is None:
        print(f"[warn] Unknown platform {sys.platform}, skipping Flet client download")
        return

    app_dir = Path(flet_desktop.__file__).resolve().parent / "app"
    dest = app_dir / artifact
    if dest.exists():
        print(f"[ok] Flet client already bundled: {dest}")
        return

    ver = flet_desktop.version.version
    url = f"https://github.com/flet-dev/flet/releases/download/v{ver}/{artifact}"
    print(f"Downloading Flet client v{ver}: {artifact} ...")
    app_dir.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, str(dest))
    print(f"[ok] Downloaded {dest.stat().st_size:,} bytes")


def main():
    _ensure_flet_client()

    args = list(NUITKA_ARGS)
    if sys.platform == "win32":
        args.insert(args.index("--assume-yes-for-downloads"), "--windows-console-mode=disable")
    if sys.platform == "darwin":
        args.insert(args.index("--assume-yes-for-downloads"), "--macos-create-app-bundle")
    if "--onefile" in sys.argv:
        args.insert(args.index("--standalone") + 1, "--onefile")
    args.append("main.py")
    subprocess.run(args, check=True)


if __name__ == "__main__":
    main()
