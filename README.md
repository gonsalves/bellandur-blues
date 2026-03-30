# Bellandur Blues

A personal article-to-podcast generator. Save interesting article links throughout the day, and listen to them as narrated podcast episodes during your commute.

## How it works

1. Paste an article URL into the web UI
2. The article is extracted and converted to speech using Edge TTS
3. Subscribe to the RSS feed in your podcast app and listen on the go

Articles are automatically routed through archive.org when a snapshot is available, which helps with paywalled content.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload
```

Open http://localhost:8000 and paste a URL.

Subscribe to the podcast feed at http://localhost:8000/feed.xml.

## Configuration

Copy `.env.example` to `.env` and edit as needed:

- `TTS_VOICE` — Edge TTS voice (run `edge-tts --list-voices` to see options)
- `BASE_URL` — Public URL of the server (used in RSS feed)
- `R2_*` — Cloudflare R2 credentials for cloud audio storage (optional, falls back to local)

## Tech stack

- **Backend**: Python, FastAPI, SQLite
- **TTS**: Edge TTS (free, no API key)
- **Article extraction**: Trafilatura
- **Audio storage**: Local filesystem or Cloudflare R2
- **Frontend**: Tailwind CSS + shadcn design tokens
