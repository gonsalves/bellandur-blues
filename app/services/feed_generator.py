from feedgen.feed import FeedGenerator
from sqlalchemy.orm import Session

from app.models import Article, ArticleStatus
from app.config import BASE_URL


def generate_feed(db: Session) -> str:
    """Build a podcast-compatible RSS feed from all ready articles."""
    fg = FeedGenerator()
    fg.load_extension("podcast")

    fg.title("Bellandur Blues")
    fg.link(href=BASE_URL)
    fg.description("Your articles, narrated as a personal podcast.")
    fg.language("en")

    fg.podcast.itunes_author("Bellandur Blues")
    fg.podcast.itunes_summary("Auto-generated podcast from saved articles.")
    fg.podcast.itunes_category("Technology")

    articles = (
        db.query(Article)
        .filter(Article.status == ArticleStatus.ready)
        .order_by(Article.created_at.desc())
        .all()
    )

    for article in articles:
        fe = fg.add_entry()
        fe.id(f"{BASE_URL}/articles/{article.id}")
        fe.title(article.title or article.url)
        fe.link(href=article.url)
        fe.description(f"Narrated version of: {article.url}")
        fe.published(article.created_at)

        if article.audio_filename:
            audio_url = f"{BASE_URL}/audio/{article.audio_filename}"
            fe.enclosure(audio_url, 0, "audio/mpeg")

            if article.audio_duration_seconds:
                fe.podcast.itunes_duration(article.audio_duration_seconds)

        if article.author:
            fe.author(name=article.author)

    return fg.rss_str(pretty=True).decode("utf-8")
