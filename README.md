# Financier Bot

Telegram expense bot with FastAPI backend and Google Sheets integration.

## Quickstart (uv)

- Install uv: https://docs.astral.sh/uv/
- Python 3.11+

```bash
# install deps
uv sync

# run API (http://127.0.0.1:8000/health)
uv run uvicorn financier_bot.main:app --reload

# run Telegram bot (requires TELEGRAM_BOT_TOKEN env)
uv run financier-bot
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
    main.py
    config.py
    routers/
      health.py
    telegram/
      bot.py
    services/
      sheets.py
```

## License

MIT
