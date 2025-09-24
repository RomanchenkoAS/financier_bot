from __future__ import annotations

import asyncio
import json
from functools import partial
from typing import Any, Dict

import gspread
from google.oauth2.service_account import Credentials
from loguru import logger

from src.config import settings


def client_from_inline_json(inline_json: str) -> gspread.Client:
    info: dict[str, Any] = json.loads(inline_json)
    creds = Credentials.from_service_account_info(
        info, scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return gspread.authorize(creds)


def append_expense(
    expense: Dict[str, Any],
    data_worksheet_name: str = "data",
    service_worksheet_name: str = "service",
) -> None:
    """
    Insert a new expense row at the top of the data table.

    The service sheet stores the index of the first data row at B2.
    We insert a new row at that index so it becomes the new first data row.
    """
    if not settings.google_service_account_json or not settings.google_spreadsheet_id:
        raise RuntimeError("Google Sheets settings are not configured")

    client = client_from_inline_json(settings.google_service_account_json.get_secret_value())
    sh = client.open_by_key(settings.google_spreadsheet_id)
    data_ws = sh.worksheet(data_worksheet_name)
    service_ws = sh.worksheet(service_worksheet_name)

    first_row_str = service_ws.acell("B2").value
    if not first_row_str:
        raise ValueError("service!B2 is empty; cannot determine first data row")
    try:
        first_data_row = int(first_row_str)
    except ValueError as exc:
        raise ValueError(f"Invalid first data row in service!B2: {first_row_str}") from exc

    row = [
        expense["date"],
        expense["category"],
        expense["amount"],
        expense["comment"],
    ]
    data_ws.insert_row(row, index=first_data_row, value_input_option="USER_ENTERED")
