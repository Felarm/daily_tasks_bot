from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import settings


async def send_user_msg_job(user_id: int, text: str):
    async with Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML)) as bot:
        await bot.send_message(chat_id=user_id, text=text)
