import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from loguru import logger

from ..config import settings


async def _main() -> None:
    token = settings.telegram_bot_token.get_secret_value() if settings.telegram_bot_token else None
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    bot = Bot(token=token)
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def on_start(msg: Message) -> None:
        await msg.answer("Привет! Пришли сумму и описание: например, '450 кофе'.")

    @dp.message()
    async def on_message(msg: Message) -> None:
        # TODO: parse message, write to sheets, return stats
        await msg.answer("Пока я только скелет. Скоро начну парсить и писать в Google Sheets.")

    logger.info("Starting Telegram bot polling")
    await dp.start_polling(bot)


def run() -> None:
    """CLI entrypoint: uv run financier-bot"""
    asyncio.run(_main())


if __name__ == "__main__":
    run()
