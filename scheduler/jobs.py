from bot.base import bot


async def send_user_msg_job(user_id: int, text: str):
    await bot.send_message(chat_id=user_id, text=text)
