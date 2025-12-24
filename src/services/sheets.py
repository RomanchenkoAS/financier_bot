from __future__ import annotations

import asyncio
import json
from datetime import datetime
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


def get_recent_expenses(limit: int = 9) -> list[dict[str, Any]]:
    """Get recent expenses from the data sheet."""
    if not settings.google_service_account_json or not settings.google_spreadsheet_id:
        raise RuntimeError("Google Sheets settings are not configured")

    client = client_from_inline_json(settings.google_service_account_json.get_secret_value())
    sh = client.open_by_key(settings.google_spreadsheet_id)
    data_ws = sh.worksheet("data")
    service_ws = sh.worksheet("service")

    # Get the first data row from service sheet
    first_row_str = service_ws.acell("B2").value
    if not first_row_str:
        raise ValueError("service!B2 is empty; cannot determine first data row")
    try:
        first_data_row = int(first_row_str)
    except ValueError as exc:
        raise ValueError(f"Invalid first data row in service!B2: {first_row_str}") from exc

    # Get data from first_data_row to first_data_row + limit
    end_row = first_data_row + limit - 1
    range_name = f"A{first_data_row}:D{end_row}"
    
    try:
        values = data_ws.get(range_name)
        expenses = []
        for row in values:
            date = str(row[0]).strip() if row[0] else ""
            category = str(row[1]).strip() if row[1] else ""
            amount = str(row[2]).strip() if row[2] else ""
            comment = str(row[3]).strip() if len(row) > 3 and row[3] else ""

            expenses.append(
                {
                    "date": date,
                    "category": category,
                    "amount": amount,
                    "comment": comment,
                }
            )
        return expenses
    except Exception as exc:
        raise ValueError(f"Failed to get recent expenses: {exc}") from exc


def get_current_month_expenses() -> list[dict[str, Any]]:
    """Get all expenses for the current month from the data sheet."""
    if not settings.google_service_account_json or not settings.google_spreadsheet_id:
        raise RuntimeError("Google Sheets settings are not configured")

    client = client_from_inline_json(settings.google_service_account_json.get_secret_value())
    sh = client.open_by_key(settings.google_spreadsheet_id)
    data_ws = sh.worksheet("data")
    service_ws = sh.worksheet("service")

    # Get the first data row from service sheet
    first_row_str = service_ws.acell("B2").value
    if not first_row_str:
        raise ValueError("service!B2 is empty; cannot determine first data row")
    try:
        first_data_row = int(first_row_str)
    except ValueError as exc:
        raise ValueError(f"Invalid first data row in service!B2: {first_row_str}") from exc

    # Get all data from first_data_row to the end (assuming max 10000 rows)
    end_row = first_data_row + 10000
    range_name = f"A{first_data_row}:D{end_row}"
    
    try:
        values = data_ws.get(range_name)
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        expenses = []
        for row in values:
            if not row or len(row) < 3:
                continue
                
            date_str = str(row[0]).strip() if row[0] else ""
            category = str(row[1]).strip() if row[1] else ""
            amount_str = str(row[2]).strip() if row[2] else ""
            comment = str(row[3]).strip() if len(row) > 3 and row[3] else ""

            # Parse date in format "DD.MM.YYYY"
            try:
                if "." in date_str:
                    parts = date_str.split(".")
                    if len(parts) == 3:
                        day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
                        # Handle two-digit years
                        if year < 100:
                            year += 2000
                        
                        # Filter by current month and year
                        if month == current_month and year == current_year:
                            try:
                                amount = float(amount_str)
                                expenses.append(
                                    {
                                        "date": date_str,
                                        "category": category,
                                        "amount": amount,
                                        "comment": comment,
                                    }
                                )
                            except (ValueError, TypeError):
                                continue
            except (ValueError, IndexError):
                continue
                
        return expenses
    except Exception as exc:
        raise ValueError(f"Failed to get current month expenses: {exc}") from exc
