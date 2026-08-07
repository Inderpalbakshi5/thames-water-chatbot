import json
import logging

from twilio.rest import Client

from .config import Settings

logger = logging.getLogger("llm_monitor.whatsapp")

# WhatsApp template variables have a much tighter length limit than freeform messages,
# so keep chunks conservative -- this size is used for both the template and freeform
# paths so behavior doesn't change based on which one happens to be active.
CHUNK_SIZE = 900


def send_whatsapp(text: str) -> None:
    if not (Settings.twilio_account_sid and Settings.twilio_auth_token and Settings.twilio_whatsapp_to):
        logger.warning("Twilio credentials not fully configured; printing digest instead:\n%s", text)
        return

    client = Client(Settings.twilio_account_sid, Settings.twilio_auth_token)
    chunks = _chunk(text, CHUNK_SIZE)
    total = len(chunks)
    for i, chunk in enumerate(chunks, start=1):
        body = chunk if total == 1 else f"({i}/{total})\n{chunk}"
        if Settings.twilio_content_sid:
            # Business-initiated WhatsApp messages need a Meta-approved template outside
            # the 24h customer-service session window -- freeform `body` sends get
            # rejected with error 21654 once that window closes, which is the normal
            # state for an unattended daily cron. See llm-release-monitor/README.md.
            client.messages.create(
                from_=Settings.twilio_whatsapp_from,
                to=Settings.twilio_whatsapp_to,
                content_sid=Settings.twilio_content_sid,
                content_variables=json.dumps({"1": body}),
            )
        else:
            client.messages.create(
                from_=Settings.twilio_whatsapp_from,
                to=Settings.twilio_whatsapp_to,
                body=body,
            )
        logger.info("Sent WhatsApp message %d/%d", i, total)


def _chunk(text: str, size: int) -> list[str]:
    if len(text) <= size:
        return [text]
    chunks = []
    remaining = text
    while remaining:
        if len(remaining) <= size:
            chunks.append(remaining)
            break
        split_at = remaining.rfind("\n", 0, size)
        if split_at <= 0:
            split_at = size
        chunks.append(remaining[:split_at])
        remaining = remaining[split_at:].lstrip("\n")
    return chunks
