import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "config" / "sources.yaml"
STATE_PATH = ROOT_DIR / "state" / "seen_items.json"

load_dotenv(ROOT_DIR / ".env")


def load_sources() -> list[dict]:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("sources", [])


class Settings:
    anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    newsapi_key = os.environ.get("NEWSAPI_KEY", "")

    twilio_account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
    twilio_auth_token = os.environ.get("TWILIO_AUTH_TOKEN", "")
    twilio_whatsapp_from = os.environ.get("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
    twilio_whatsapp_to = os.environ.get("TWILIO_WHATSAPP_TO", "")

    send_on_empty = os.environ.get("SEND_ON_EMPTY", "false").strip().lower() == "true"

    # Test-mode knobs, both off by default so normal/scheduled runs are unaffected.
    # LOOKBACK_HOURS widens the "published in the last N hours" filter beyond 24h, and
    # IGNORE_SEEN skips the already-seen-before check -- together they let an old, real
    # item flow through summarize -> WhatsApp for an end-to-end smoke test. Test runs never
    # write to state/seen_items.json, so they can't affect what a real run reports later.
    lookback_hours = int(os.environ.get("LOOKBACK_HOURS", "24"))
    ignore_seen = os.environ.get("IGNORE_SEEN", "false").strip().lower() == "true"
