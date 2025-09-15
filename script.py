import os
import sys
from datetime import datetime

from loguru import logger

from src.services.sheets import client_from_inline_json
from dotenv import load_dotenv

load_dotenv()


def main() -> int:
    service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    spreadsheet_id = os.getenv("GOOGLE_SPREADSHEET_ID")
    worksheet_name = os.getenv("GOOGLE_WORKSHEET_NAME", "Expenses")

    if not spreadsheet_id:
        logger.error("Missing required env var: GOOGLE_SPREADSHEET_ID")
        return 1

    try:
        client = client_from_inline_json(service_account_json)

        sh = client.open_by_key(spreadsheet_id)
        ws = sh.worksheet(worksheet_name)

        value = f"Health check OK @ {datetime.now().isoformat(timespec='seconds')}"
        # Write to A1
        ws.update_acell("A1", value)
        logger.info(f"Successfully wrote to {worksheet_name}!A1: {value}")
        return 0
    except Exception as e:
        logger.exception("Failed to write to Google Sheets")
        return 2


if __name__ == "__main__":
    sys.exit(main())
