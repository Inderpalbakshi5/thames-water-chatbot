import logging

import feedparser
import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from .config import Settings
from .models import NewsItem

logger = logging.getLogger("llm_monitor.fetchers")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}
TIMEOUT = 20


def fetch_source(source: dict) -> list[NewsItem]:
    """Dispatch to the right fetcher for one config entry. Never raises -- a broken
    source should not take the rest of the run down with it."""
    name = source.get("name", "unknown")
    source_type = source.get("type")
    try:
        if source_type == "github_releases":
            return _fetch_github_releases(name, source["repo"])
        if source_type == "newsapi":
            return _fetch_newsapi(name, source["query"], source.get("domains", ""))
        if source_type == "html":
            return _fetch_html(name, source["url"])
        logger.warning("Unknown source type %r for %s, skipping", source_type, name)
        return []
    except Exception as exc:  # noqa: BLE001 - one bad source must not kill the run
        logger.warning("Failed to fetch source %s (%s): %s", name, source_type, exc)
        return []


def _fetch_github_releases(name: str, repo: str) -> list[NewsItem]:
    url = f"https://github.com/{repo}/releases.atom"
    feed = feedparser.parse(url, request_headers=HEADERS)
    items = []
    for entry in feed.entries:
        published = entry.get("updated") or entry.get("published")
        if not published:
            continue
        published_dt = date_parser.parse(published)
        items.append(
            NewsItem(
                source_name=name,
                title=entry.get("title", repo),
                url=entry.get("link", url),
                published_at=published_dt,
                snippet=(entry.get("summary") or "")[:500],
            )
        )
    return items


def _fetch_newsapi(name: str, query: str, domains: str) -> list[NewsItem]:
    if not Settings.newsapi_key:
        logger.info("NEWSAPI_KEY not set, skipping newsapi source %s", name)
        return []
    params = {
        "q": query,
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": 20,
        "apiKey": Settings.newsapi_key,
    }
    if domains:
        params["domains"] = domains
    resp = requests.get(
        "https://newsapi.org/v2/everything", params=params, headers=HEADERS, timeout=TIMEOUT
    )
    try:
        resp.raise_for_status()
    except requests.HTTPError as exc:
        # Re-raise without the request URL (it contains the API key as a query param) --
        # the response body alone has NewsAPI's actual error code/message and is safe to log.
        raise RuntimeError(f"NewsAPI HTTP {resp.status_code}: {resp.text[:300]}") from exc
    payload = resp.json()
    items = []
    for article in payload.get("articles", []):
        published = article.get("publishedAt")
        if not published:
            continue
        items.append(
            NewsItem(
                source_name=name,
                title=article.get("title", name),
                url=article.get("url", ""),
                published_at=date_parser.parse(published),
                snippet=(article.get("description") or "")[:500],
            )
        )
    return items


def _fetch_html(name: str, url: str) -> list[NewsItem]:
    """Best-effort scrape for pages with no feed and no NewsAPI coverage. Looks for
    <time datetime="..."> elements and takes the nearest link/heading as the title.
    Sites behind bot protection (Cloudflare etc.) or that render via JS will return
    zero items here -- that's a silent skip, not an error, by design."""
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    items = []
    for time_tag in soup.find_all("time"):
        datetime_attr = time_tag.get("datetime")
        if not datetime_attr:
            continue
        try:
            published_dt = date_parser.parse(datetime_attr)
        except (ValueError, OverflowError):
            continue

        link_tag = time_tag.find_parent("a") or time_tag.find_next("a")
        if link_tag and link_tag.get("href"):
            href = link_tag["href"]
            title = link_tag.get_text(strip=True) or href
        else:
            href = url
            title = time_tag.get_text(strip=True) or name

        if href.startswith("/"):
            base = "/".join(url.split("/")[:3])
            href = base + href

        items.append(
            NewsItem(source_name=name, title=title, url=href, published_at=published_dt)
        )
    return items
