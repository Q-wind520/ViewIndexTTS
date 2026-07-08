# AGENTS.md — ATRI-IndexTTS-GUI

## Repo layout

```
backend/ATRI-IndexTTS/   # git submodule → github.com/Q-wind520/ATRI-IndexTTS.git
                         #   Core Python library (atri-indextts)
gui/                     # Flet desktop GUI (replaces old Flutter frontend)
```

## GUI (Flet)

- **Run**: `& ".venv/Scripts/python.exe" main.py` (from repo root)
- **Directly imports** `atri_indextts` (no HTTP layer needed)
- **Deps in root venv**: flet, simpleaudio, atri-indextts (editable)
- **UI**: single-page: text input → provider/voice/prompt selection → emotion controls → synthesize → play
- **Config**: `.env` at project root for API keys, `~/.config/indextts/config.json` for non-sensitive

## Backend (atri-indextts)

See `backend/ATRI-IndexTTS/AGENTS.md`. Key shortcuts:

```powershell
# Run CLI
python -m uv run --directory backend/ATRI-IndexTTS indextts tts "你好"

# Test
python -m uv run --directory backend/ATRI-IndexTTS pytest

# Lint
python -m uv run --directory backend/ATRI-IndexTTS ruff check .
python -m uv run --directory backend/ATRI-IndexTTS ruff format .
```

## Gotchas

- `backend/ATRI-IndexTTS` is a **git submodule** — changes there belong to upstream
- Root venv at `.venv/` was built with Python 3.12
- After pulling submodule changes: `pip install -e backend/ATRI-IndexTTS` in root venv
- API keys go in `.env` at repo root (copy from `gui/.env.example`)
