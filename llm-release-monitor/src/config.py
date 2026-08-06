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
