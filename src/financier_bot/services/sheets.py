from __future__ import annotations

import json
from typing import Any

import gspread
from google.oauth2.service_account import Credentials


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
