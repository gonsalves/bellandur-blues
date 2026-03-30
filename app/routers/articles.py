from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl

from app.database import get_db
from app.models import Article, ArticleStatus
from app.services.extractor import extract_article
from app.services.tts import generate_audio

router = APIRouter(prefix="/articles", tags=["articles"])


class ArticleCreate(BaseModel):
    url: HttpUrl


class ArticleResponse(BaseModel):
    id: int
    url: str
    title: Optional[str]
    author: Optional[str]
    status: ArticleStatus
    error: Optional[str]
    audio_filename: Optional[str]
    audio_duration_seconds: Optional[int]

    class Config:
        from_attributes = True


def _process_article(article_id: int):
    """Background task: extract article content, then generate audio."""
    db = next(get_db())
    try:
        article = db.query(Article).get(article_id)
        if not article:
            return

        # Step 1: Extract
        article.status = ArticleStatus.extracting
        db.commit()

        result = extract_article(article.url)
        article.title = result["title"]
        article.author = result["author"]
        article.text = result["text"]
        article.status = ArticleStatus.extracted
        db.commit()

        # Step 2: Generate audio
        article.status = ArticleStatus.generating
        db.commit()

        filename, duration = generate_audio(article.text)
        article.audio_filename = filename
        article.audio_duration_seconds = duration
        article.status = ArticleStatus.ready
        db.commit()

    except Exception as e:
        article.status = ArticleStatus.failed
        article.error = str(e)
        db.commit()
    finally:
        db.close()


@router.post("", response_model=ArticleResponse, status_code=201)
def add_article(
    body: ArticleCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    existing = db.query(Article).filter(Article.url == str(body.url)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Article already exists")

    article = Article(url=str(body.url))
    db.add(article)
    db.commit()
    db.refresh(article)

    background_tasks.add_task(_process_article, article.id)
    return article


@router.get("", response_model=list[ArticleResponse])
def list_articles(db: Session = Depends(get_db)):
    return db.query(Article).order_by(Article.created_at.desc()).all()


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(Article).get(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.delete("/{article_id}", status_code=204)
def delete_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(Article).get(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    db.delete(article)
    db.commit()


@router.post("/{article_id}/regenerate", response_model=ArticleResponse)
def regenerate_audio(
    article_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    article = db.query(Article).get(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    article.status = ArticleStatus.pending
    article.error = None
    db.commit()
    db.refresh(article)

    background_tasks.add_task(_process_article, article.id)
    return article
