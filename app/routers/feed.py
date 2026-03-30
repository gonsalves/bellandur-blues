from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.feed_generator import generate_feed

router = APIRouter(tags=["feed"])


@router.get("/feed.xml")
def podcast_feed(db: Session = Depends(get_db)):
    xml = generate_feed(db)
    return Response(content=xml, media_type="application/rss+xml")
