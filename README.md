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
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account", ...}
GOOGLE_SPREADSHEET_ID=your_sheet_id
GOOGLE_WORKSHEET_NAME=Expenses
```

## Structure

```
src/
  financier_bot/
    config.py
    telegram/
      bot.py
    services/
      sheets.py
```
