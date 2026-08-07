import logging
from datetime import datetime, timedelta, timezone

from .config import Settings, load_sources
from .fetchers import fetch_source
from .state_store import load_seen, save_seen
from .summarizer import summarize
from .whatsapp import send_whatsapp

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("llm_monitor.main")


def run() -> None:
    sources = load_sources()
    seen = load_seen()
    cutoff = datetime.now(timezone.utc) - timedelta(hours=Settings.lookback_hours)
    if Settings.ignore_seen or Settings.lookback_hours != 24:
        logger.info(
            "Test mode: lookback_hours=%d ignore_seen=%s (state will not be updated)",
            Settings.lookback_hours,
            Settings.ignore_seen,
        )

    new_items = []
    for source in sources:
        fetched = fetch_source(source)
        logger.info("Fetched %d item(s) from %s", len(fetched), source.get("name"))
        for item in fetched:
            published = item.published_at
            if published.tzinfo is None:
                published = published.replace(tzinfo=timezone.utc)
            if published < cutoff:
                continue
            if not Settings.ignore_seen and item.key in seen:
                continue
            new_items.append(item)

    if not new_items:
        logger.info("No new releases in the lookback window.")
        if Settings.send_on_empty:
            send_whatsapp("LLM release digest: no new releases in the past 24 hours.")
        return

    logger.info("Found %d new item(s), summarizing...", len(new_items))
    digest = summarize(new_items)
    send_whatsapp(digest)

    if Settings.ignore_seen:
        return  # test run -- don't let it affect what a real run reports later

    now_iso = datetime.now(timezone.utc).isoformat()
    for item in new_items:
        seen[item.key] = now_iso
    save_seen(seen)


if __name__ == "__main__":
    run()
