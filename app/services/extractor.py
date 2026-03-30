import httpx
import trafilatura

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


def _get_archive_url(url: str) -> str:
    """Look up the latest archive.org snapshot for a URL.

    Returns the archived URL if available, otherwise returns the original URL.
    """
    if "web.archive.org" in url:
        return url

    try:
        resp = httpx.get(
            "https://archive.org/wayback/available",
            params={"url": url},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        snapshot = data.get("archived_snapshots", {}).get("closest", {})
        if snapshot.get("available") and snapshot.get("status") == "200":
            return snapshot["url"]
    except Exception:
        pass

    return url


def _fetch(url: str) -> str:
    """Fetch URL content, trying trafilatura first then httpx as fallback."""
    downloaded = trafilatura.fetch_url(url)
    if downloaded:
        return downloaded

    response = httpx.get(url, headers=_HEADERS, follow_redirects=True, timeout=30)
    response.raise_for_status()
    return response.text


def extract_article(url: str) -> dict:
    """Fetch a URL and extract the article content.

    All URLs are routed through archive.org when a snapshot is available,
    which helps with paywalled content.
    """
    fetch_url = _get_archive_url(url)
    html = _fetch(fetch_url)

    text = trafilatura.extract(html, include_comments=False, include_tables=False)
    if not text:
        raise ValueError("Could not extract article content from: {}".format(url))

    metadata = trafilatura.extract_metadata(html)

    return {
        "title": metadata.title if metadata else None,
        "author": metadata.author if metadata else None,
        "text": text,
    }
