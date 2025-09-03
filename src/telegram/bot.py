import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from loguru import logger

from src.config import settings

class Chat:
    def __init__(self, msg: Message):
        self.bot = msg.bot
        self.chat_id = msg.chat.id
        
    def _is_allowed(self) -> bool:
        allowed = settings.allowed_chat_id
        return allowed is None or self.chat_id == allowed
    
    async def respond(self, text: str) -> None:
        await self.bot.send_message(self.chat_id, text)


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
        # TODO: parse message, write to sheets, return stats
        
        await chat.respond("Пока я только скелет. Скоро начну парсить и писать в Google Sheets.")

    logger.info("Starting Telegram bot polling")
    await dp.start_polling(bot)


def run() -> None:
    """CLI entrypoint: uv run financier-bot"""
    asyncio.run(_main())


if __name__ == "__main__":
    run()
