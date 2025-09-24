"""Telegram bot utility functions."""

from typing import Any, Dict


def format_expense_for_display(expense: Dict[str, Any], index: int = None) -> str:
    """Format an expense for display in chat messages."""
    date = expense.get("date", "").strip()
    category = expense.get("category", "").strip()
    amount = expense.get("amount", "").strip()
    comment = expense.get("comment", "").strip()

    # Format amount as number
    try:
        amount_str = f"{float(amount):.0f}" if amount else ""
    except (ValueError, TypeError):
        amount_str = str(amount) if amount else ""

    # Build the display string
    parts = []
    if index is not None:
        parts.append(f"{index}.")

    parts.append(f"💰 {str(amount_str).rjust(6)}\t")
    parts.append(f"📂 {category}\t")

    if date:
        parts.append(f"📅 {str(date).rjust(10)}\t")

    # Only show comment if it's not empty
    if comment:
        parts.append(f"💬 {comment}")

    return " ".join(parts)


def get_example_formats() -> list[str]:
    """Get example input formats for the /example command."""
    return [
        '450 кофе',
        '500 Транспорт "Такси"',
        '450 кофе 01.09.25',
        '450 кофе 01/09/25',
        '450 кофе 01-09-25',
        '450 кофе 01.09',
        '450 кофе 01.09.25 "пиво"',
        '450 кофе "пиво" 01.09.25',
    ]
