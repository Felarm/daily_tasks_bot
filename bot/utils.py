from typing import Any

from aiogram.fsm.context import FSMContext


async def pop_from_fsm_ctx_by_key(key: str, state_data: FSMContext) -> Any:
    ctx_data = await state_data.get_data()
    value = ctx_data.pop(key)
    await state_data.set_data(ctx_data)
    return value