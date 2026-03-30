from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, RedirectResponse

from app.config import AUDIO_DIR
from app.services.storage import _r2_enabled, get_audio_url

router = APIRouter(tags=["audio"])


@router.get("/audio/{filename}")
def serve_audio(filename: str):
    if _r2_enabled():
        return RedirectResponse(url=get_audio_url(filename))

    filepath = AUDIO_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(str(filepath), media_type="audio/mpeg")
