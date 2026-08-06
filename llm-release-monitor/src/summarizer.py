from anthropic import Anthropic

from .config import Settings
from .models import NewsItem

MODEL = "claude-sonnet-5"

SYSTEM_PROMPT = """You write a short daily WhatsApp digest of LLM industry releases.
Input is a list of raw article/release items from the last 24 hours, each tagged with
its source company. Group by company. For each item write one crisp bullet: what
shipped/changed, skip marketing fluff. Drop items that are clearly not an actual
release/update/model announcement (e.g. unrelated news that matched a keyword search).
Keep the whole message under 1500 characters so it fits in a single WhatsApp message.
Use plain text only -- no markdown headers, just company names in CAPS or with emoji,
and "-" for bullets. End with nothing extra, no sign-off."""


def summarize(items: list[NewsItem]) -> str:
    if not Settings.anthropic_api_key:
        return _fallback_digest(items)

    client = Anthropic(api_key=Settings.anthropic_api_key)
    raw = "\n\n".join(
        f"[{item.source_name}] {item.title}\n{item.url}\n{item.snippet}" for item in items
    )
    message = client.messages.create(
        model=MODEL,
        max_tokens=800,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": raw}],
    )
    return "".join(block.text for block in message.content if block.type == "text").strip()


def _fallback_digest(items: list[NewsItem]) -> str:
    """No ANTHROPIC_API_KEY configured -- emit a plain grouped list instead of failing."""
    by_source: dict[str, list[NewsItem]] = {}
    for item in items:
        by_source.setdefault(item.source_name, []).append(item)

    lines = ["LLM release digest (raw, no summarization key set):"]
    for source_name, source_items in by_source.items():
        lines.append(f"\n{source_name}:")
        for item in source_items:
            lines.append(f"- {item.title} ({item.url})")
    return "\n".join(lines)
