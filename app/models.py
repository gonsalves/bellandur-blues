from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime, timezone
import enum


class Base(DeclarativeBase):
    pass


class ArticleStatus(str, enum.Enum):
    pending = "pending"
    extracting = "extracting"
    extracted = "extracted"
    generating = "generating"
    ready = "ready"
    failed = "failed"


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=True)
    author = Column(String, nullable=True)
    text = Column(Text, nullable=True)
    status = Column(SAEnum(ArticleStatus), default=ArticleStatus.pending, nullable=False)
    error = Column(Text, nullable=True)
    audio_filename = Column(String, nullable=True)
    audio_duration_seconds = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
