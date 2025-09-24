import asyncio
import re
from datetime import datetime
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from loguru import logger

from src.config import settings
from src.services.sheets import append_expense


class Chat:
    def __init__(self, msg: Message):
        self.bot = msg.bot
        self.chat_id = msg.chat.id

    def _is_allowed(self) -> bool:
        allowed = settings.allowed_chat_id
        return allowed is None or self.chat_id == allowed

    async def respond(self, text: str) -> None:
        await self.bot.send_message(self.chat_id, text)

    async def _parse_message(self, message: str) -> dict[str, Any]:
        """
        Possible keys:
        - amount: required
        - category: required
        - date: optional
        - comment: optional

        todo: in future learn to parse 'Транспорт 990 09.09 "такси"'
        """
        result = {}

        # Extract comment if present
        comment_pattern = r'["\'\`<](.*?)["\'\`>]'
        comment_match = re.search(comment_pattern, message)

        if comment_match:
            result["comment"] = comment_match.group(1)
            # Remove the comment from the message for further processing
            message = re.sub(comment_pattern, "", message).strip()
        else:
            result["comment"] = ""

        # Extract date if present
        date_pattern = r"(\d{1,2}[./-]\d{1,2}(?:[./-]\d{2,4})?)"
        date_match = re.search(date_pattern, message)

        if date_match:
            date_str = date_match.group(1)
            # Remove the date from the message for further processing
            message = message.replace(date_str, "").strip()

            # Parse the date
            try:
                # Handle different date formats
                if "." in date_str:
                    parts = date_str.split(".")
                elif "/" in date_str:
                    parts = date_str.split("/")
                elif "-" in date_str:
                    parts = date_str.split("-")
                else:
                    raise ValueError(f"Unsupported date format: {date_str}")

                day = int(parts[0])
                month = int(parts[1])

                # If year is provided, use it; otherwise use current year
                current_year = datetime.now().year
                if len(parts) > 2:
                    year = int(parts[2])
                    # Handle two-digit years
                    if year < 100:
                        year += 2000
                else:
                    year = current_year

                result["date"] = datetime(year, month, day).strftime("%Y-%m-%d")
            except (ValueError, IndexError):
                raise ValueError(f"Invalid date format: {date_str}")
        else:
            # Use today's date if no date provided
            result["date"] = datetime.now().strftime("%Y-%m-%d")

        # Split the remaining message into words
        words = message.split()
        if len(words) < 2:
            raise ValueError("Message must contain at least amount and category")

        # First word should be the amount
        try:
            result["amount"] = float(words[0])
        except ValueError:
            raise ValueError(f"Invalid amount: {words[0]}")

        # The rest is the category
        result["category"] = " ".join(words[1:])

        return result


async def _main() -> None:
    token = settings.telegram_bot_token.get_secret_value() if settings.telegram_bot_token else None
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    bot = Bot(token=token)
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def on_start(msg: Message) -> None:
        chat = Chat(msg)
        logger.info(f"/start from chat_id={chat.chat_id}")
        if not chat._is_allowed():
            await chat.respond("Access denied for this chat.")
            return
        await chat.respond(
            f"Привет! Твой chat_id: {chat.chat_id}.\n"
            "Пришли сумму и описание: например, '450 кофе'."
        )

    @dp.message()
    async def on_message(msg: Message) -> None:
        chat = Chat(msg)
        if not chat._is_allowed():
            return

        try:
            parsed_data = await chat._parse_message(msg.text)

            response = (
                f"✅ Parsed successfully:\n"
                f"💰 Amount: {parsed_data['amount']}\n"
                f"📂 Category: {parsed_data['category']}\n"
                f"📅 Date: {parsed_data['date']}"
            )

            if parsed_data["comment"]:
                response += f"\n💬 Comment: {parsed_data['comment']}"

            try:
                append_expense(parsed_data)
                response += "\n\n✅ Saved to Google Sheets"
            except Exception as e:
                logger.error(f"Failed to save to Google Sheets: {e}")
                response += f"\n\n❌ Failed to save to Google Sheets: {str(e)}"

            await chat.respond(response)

        except ValueError as e:
            await chat.respond(f"❌ Error: {str(e)}")

    logger.info("Starting Telegram bot polling")
    await dp.start_polling(bot)


def run() -> None:
    """CLI entrypoint: uv run financier-bot"""
    asyncio.run(_main())


if __name__ == "__main__":
    run()
