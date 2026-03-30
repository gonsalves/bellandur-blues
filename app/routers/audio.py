from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.config import AUDIO_DIR

router = APIRouter(tags=["audio"])


@router.get("/audio/{filename}")
def serve_audio(filename: str):
    filepath = AUDIO_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(str(filepath), media_type="audio/mpeg")
