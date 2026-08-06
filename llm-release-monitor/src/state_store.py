import json
from datetime import datetime, timedelta, timezone

from .config import STATE_PATH

# Keep seen-item records around for a week; anything older is irrelevant for a
# "new in the last 24h" filter and would just make the state file grow forever.
RETENTION_DAYS = 7


def load_seen() -> dict[str, str]:
    if not STATE_PATH.exists():
        return {}
    with open(STATE_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_seen(seen: dict[str, str]) -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)
    pruned = {
        key: seen_at
        for key, seen_at in seen.items()
        if datetime.fromisoformat(seen_at) >= cutoff
    }
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(pruned, f, indent=2, sort_keys=True)
