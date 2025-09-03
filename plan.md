# Development plan

## Parsing logic

- Parse messages like:
  - "450 кофе"
  - "1200 продукты 2025-09-01"
  - "15$ lunch" (detect currency if present)
    -Extract: amount, currency (default), category, note, date (default: today).
- Normalize text (ru/en), handle decimals and separators.

## Sheets integration

- Append rows: timestamp, user_id, amount, currency, category, note, date.
- Retry with backoff.

## Stats reply

- Compute daily/weekly/monthly totals and by category from the sheet.
- Reply after write with a compact summary.

## Quality

- Lint: ruff; types: mypy; CI: GitHub Actions.
