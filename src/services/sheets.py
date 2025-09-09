from __future__ import annotations

import json
from typing import Any, Dict
import asyncio
from functools import partial

import gspread
from google.oauth2.service_account import Credentials
from loguru import logger


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]


def client_from_inline_json(inline_json: str) -> gspread.Client:
    info: dict[str, Any] = json.loads(inline_json)
    creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    return gspread.authorize(creds)


def append_expense(client: gspread.Client, spreadsheet_id: str, worksheet_name: str, row: list[Any]) -> None:
    sh = client.open_by_key(spreadsheet_id)
    ws = sh.worksheet(worksheet_name)
    ws.append_row(row, value_input_option="USER_ENTERED")


async def async_append_expense(client: gspread.Client, spreadsheet_id: str, worksheet_name: str, row: list[Any]) -> None:
    """Async wrapper for append_expense"""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None, 
        partial(append_expense, client, spreadsheet_id, worksheet_name, row)
    )


async def format_expense_row(expense_data: Dict[str, Any]) -> list[Any]:
    """Format expense data as a row for Google Sheets"""
    return [
        expense_data["date"],
        expense_data["amount"],
        expense_data["category"],
        expense_data["comment"] or ""
    ]
