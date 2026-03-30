import trafilatura


def extract_article(url: str) -> dict:
    """Fetch a URL and extract the article content."""
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        raise ValueError(f"Could not fetch URL: {url}")

    text = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
    if not text:
        raise ValueError(f"Could not extract article content from: {url}")

    metadata = trafilatura.extract_metadata(downloaded)

    return {
        "title": metadata.title if metadata else None,
        "author": metadata.author if metadata else None,
        "text": text,
    }
