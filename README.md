# Financier Bot

Telegram expense bot with FastAPI backend and Google Sheets integration.

## Quickstart (uv)

- Install uv: https://docs.astral.sh/uv/
- Python 3.11+

```bash
uv sync
uv run python -m src.telegram.bot
```

- if you need hot reload

```bash
uv run watchfiles "uv run python -m src.telegram.bot" src/
```

## Environment

Copy `.env.example` to `.env` and fill values:

```env
TELEGRAM_BOT_TOKEN=xxxxx
ALLOWED_CHAT_ID=123456789
WEBAPP_URL=https://your-public-domain.example
WEBAPP_INIT_DATA_MAX_AGE_SECONDS=300
BOT_BACKEND_HOST=0.0.0.0
BOT_BACKEND_PORT=8000
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account", ...}
GOOGLE_SPREADSHEET_ID=your_sheet_id
GOOGLE_WORKSHEET_NAME=Expenses
```

`WEBAPP_URL` must be a public HTTPS URL. Telegram Mini App will not open from localhost.

## Commands

- `/example` - input examples
- `/recent` - recent expenses
- `/stats` - current month text stats + Mini App button
- `/app` - open Mini App directly
- Telegram menu button - opens Mini App directly (configured automatically when `WEBAPP_URL` is set)

## Mini App setup

1. Expose backend to public HTTPS domain (for local dev use tunnel like ngrok or cloudflared).
2. Set `WEBAPP_URL` to your Mini App root URL, for example `https://abc123.ngrok-free.app`.
3. Start the bot:

```bash
uv run python -m src.telegram.bot
```

4. In Telegram open chat with bot and run `/app` or `/stats`.

## Structure

```
src/
  config.py
  webapp.py
  telegram/
    bot.py
  services/
    sheets.py
```
