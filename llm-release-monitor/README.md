# LLM Release Monitor

Checks a list of AI labs (OpenAI, Anthropic, Google DeepMind, Meta AI, xAI, Mistral,
DeepSeek, Qwen, Kimi/Moonshot, GLM) daily for anything published in the last 24 hours,
writes a short consolidated digest with Claude, and sends it to your WhatsApp via the
Twilio sandbox.

Runs on a daily GitHub Actions cron ([`.github/workflows/llm-release-digest.yml`](../.github/workflows/llm-release-digest.yml)
at the repo root). Can also be run locally / on any other scheduler.

## How it finds "new" items

Two source types, defined in [`config/sources.yaml`](config/sources.yaml):

- **`github_releases`** — reads `https://github.com/<org>/<repo>/releases.atom`. No API
  key, very reliable. Used for labs that ship on GitHub (DeepSeek, Qwen, Kimi, Llama, GLM,
  Mistral).
- **`newsapi`** — queries [NewsAPI.org](https://newsapi.org), scoped to the provider's own
  domain. Used for the closed-lab corporate blogs (OpenAI, Anthropic, Google, Meta AI, xAI,
  Mistral), because those sites returned `403 Forbidden` to a plain HTTP fetch during setup
  (bot protection) and several are JS-rendered SPAs, so scraping them directly isn't
  reliable. Requires `NEWSAPI_KEY`; sources of this type are **skipped, not failed**, if the
  key is unset, so the rest of the run still works.

There's also a zero-dependency `html` fetcher type (`src/fetchers.py`) you can opt into per
source if you find a provider page that isn't behind bot protection — best-effort only,
may break if the page layout changes.

A source publishing something is not enough on its own: an item is only included if it (a)
was published in the last 24 hours **and** (b) its URL hasn't been seen in a previous run
(tracked in `state/seen_items.json`, committed back to the repo by the workflow after each
run, pruned after 7 days).

## Setup

### 1. Twilio WhatsApp sandbox
1. Sign up at [twilio.com](https://www.twilio.com), open Console → Messaging → Try it out →
   Send a WhatsApp message.
2. From your WhatsApp, send the shown `join <code>` phrase to `+1 415 523 8886`. This opts
   your number into the sandbox (needed once; sandbox sessions can expire and need
   rejoining — Twilio will tell you if that happens).
3. Note your **Account SID** and **Auth Token** from the Console dashboard.

### 1b. WhatsApp message template (required for daily unattended sends)
WhatsApp only allows **freeform** business-initiated text within 24 hours of the
recipient's last message. A once-a-day cron almost never runs inside that window, so
without a template, sends fail with Twilio error `21654: ContentSid Required` on any day
you haven't personally messaged the sandbox first. This applies outside the sandbox too —
it's a WhatsApp platform rule, not a sandbox-specific limitation.

1. Twilio Console → **Messaging → Content Editor** → **Create new** → channel **WhatsApp**,
   type **Text**.
2. Body:
   ```
   🤖 LLM Release Digest

   {{1}}
   ```
3. Submit for WhatsApp approval, category **Utility**. Approval is handled by Meta via
   Twilio, typically within a few hours to about a day.
4. Once approved, copy the template's **Content SID** (starts with `HX...`) — that's
   `TWILIO_CONTENT_SID` below.

Until it's approved, the bot falls back to freeform sends, which work fine for one-off
tests right after you've messaged the sandbox, but will intermittently fail for the
scheduled daily run.

### 2. NewsAPI.org key (optional but recommended)
Free at [newsapi.org/register](https://newsapi.org/register). Without it, only the
GitHub-releases sources (DeepSeek, Qwen, Kimi, Llama, GLM, Mistral) are checked.

### 3. Anthropic API key (optional but recommended)
Without it, the digest falls back to a plain grouped list of raw items instead of a
written summary.

### 4. Configure secrets

**For GitHub Actions** (Settings → Secrets and variables → Actions → New repository
secret), add:
- `ANTHROPIC_API_KEY`
- `NEWSAPI_KEY`
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_WHATSAPP_FROM` (sandbox default: `whatsapp:+14155238886`)
- `TWILIO_WHATSAPP_TO` (your number, e.g. `whatsapp:+919876543210`)
- `TWILIO_CONTENT_SID` (from step 1b above, once approved — omit to fall back to freeform)

**For local runs**, copy `.env.example` to `.env` and fill in the same values.

### 5. Run it
```bash
cd llm-release-monitor
pip install -r requirements.txt
python -m src.main
```

Or trigger the GitHub Actions workflow manually the first time (Actions tab →
"LLM Release Digest" → Run workflow) to confirm it's wired up correctly before waiting for
the daily 07:00 UTC schedule.

## Adding / removing providers

Edit `config/sources.yaml`. No code changes needed for `github_releases` or `newsapi`
entries — just add a block following the existing examples.

## Known limitations

- The Twilio **sandbox** is fine for sending to your own verified number indefinitely, but
  is not meant for messaging other people — upgrading to a production WhatsApp sender
  requires Meta business verification (message templates are needed either way, see 1b).
- Without an approved `TWILIO_CONTENT_SID`, the scheduled daily run will intermittently
  fail with Twilio error 21654 once the 24h session window closes — see setup step 1b.
- `newsapi` search is keyword-based, not a guaranteed feed of official announcements — the
  summarizer prompt is told to drop obviously irrelevant matches, but some noise is
  possible.
- The optional `html` fetcher will silently return zero items on any page with bot
  protection or client-side rendering — treat it as a bonus, not the primary path, for
  the corporate blogs.
