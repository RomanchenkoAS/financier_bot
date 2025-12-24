"""Telegram bot utility functions."""

from collections import defaultdict
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


def format_stats(expenses: list[dict[str, Any]]) -> str:
    """Format statistics for display in chat messages."""
    if not expenses:
        return "📊 Нет данных за текущий месяц"
    
    # Calculate total
    total = sum(exp.get("amount", 0) for exp in expenses)
    
    # Calculate per day average
    # Get unique dates
    unique_dates = set(exp.get("date", "") for exp in expenses if exp.get("date"))
    days_count = len(unique_dates) if unique_dates else 1
    per_day_avg = total / days_count if days_count > 0 else 0
    
    # Calculate category subtotals
    category_totals = defaultdict(float)
    for exp in expenses:
        category = exp.get("category", "").strip()
        amount = exp.get("amount", 0)
        if category:
            category_totals[category] += amount
    
    # Sort categories by subtotal in descending order
    sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    
    # Format the response
    response = "📈 Статистика за текущий месяц\n\n"
    response += f"💰 Всего: {total:.0f}\n"
    response += f"📅 Среднее в день: {per_day_avg:.0f}\n\n"
    response += "📂 Категории:\n"
    
    for category, subtotal in sorted_categories:
        response += f"• {category} - {subtotal:.0f}\n"
    
    return response
