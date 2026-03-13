from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.users.keyboards import main_user_kb
from bot.users.schemas import NewUserSchema
from user.service import UserService

user_router = Router()


@user_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    registered_user = await UserService.get_user_by_tg_id(message.from_user.id)
    if registered_user is None:
        new_user = NewUserSchema(
            tg_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )
        await UserService.register_new_user(**new_user.model_dump())
    await message.answer("welcome!", reply_markup=main_user_kb())
