from datetime import datetime, timedelta, time

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode

from bot.daily_tasks.new_tasks_creation.states import DailyTaskCreationStates, DailyTaskCopyStates
from bot.daily_tasks.keyboards import KbDTPlanRoutes, DTPlanActions, DTProgressActions, KbDTProgressRoutes, \
    task_control_kb
from bot.daily_tasks.schemas import DTProgressSchema
from bot.users.keyboards import main_user_kb
from bot.utils import pop_from_fsm_ctx_by_key
from daily_task.service import DailyTaskService
from notifier.events import DTaskNotifyEventTypes
from notifier.tg_notifier import TgDTaskNotifier, TgUserNotifierSettings

plan_task_router = Router()
control_task_state_router = Router()


@plan_task_router.callback_query(F.data == KbDTPlanRoutes.new_daily_task)
async def start_create_task_dialog(callback: CallbackQuery, dialog_manager: DialogManager):
    await dialog_manager.start(state=DailyTaskCreationStates.name, mode=StartMode.RESET_STACK)


@plan_task_router.callback_query(DTPlanActions.filter(F.action == KbDTPlanRoutes.delete_task))
async def delete_task(callback: CallbackQuery, callback_data: DTPlanActions):
    task_id = callback_data.task_id
    await DailyTaskService.delete_task(task_id=task_id)
    TgDTaskNotifier.delete_dt_jobs(task_id)
    await callback.message.answer(f"deleted task with {task_id=}", reply_markup=main_user_kb())


@plan_task_router.callback_query(DTPlanActions.filter(F.action == KbDTPlanRoutes.copy_task_to_date))
async def start_copy_task_dialog(callback: CallbackQuery, callback_data: DTPlanActions, dialog_manager: DialogManager):
    task = await DailyTaskService.get_task(callback_data.task_id)
    await dialog_manager.start(
        state=DailyTaskCopyStates.new_task_start_date,
        data={"task_to_copy": task.to_dict(exclude_none=True)},
        mode=StartMode.RESET_STACK,
    )


@control_task_state_router.callback_query(DTProgressActions.filter(F.action == KbDTProgressRoutes.approve_task))
async def approve_progress(callback: CallbackQuery, callback_data: DTProgressActions, state: FSMContext):
    await pop_from_fsm_ctx_by_key(str(callback_data.task_id), state)
    if callback_data.event == DTaskNotifyEventTypes.start_dialog:
        await DailyTaskService.begin_task(callback_data.task_id, datetime.now())
        await callback.message.answer("ok, lets rooolll")
    elif callback_data.event == DTaskNotifyEventTypes.end_dialog:
        await DailyTaskService.end_task(callback_data.task_id, datetime.now())
        await callback.message.answer("yay, you did it")
    else:
        await callback.message.answer("hmm.. this button works with created or started task states only")


@control_task_state_router.callback_query(DTProgressActions.filter(F.action == KbDTProgressRoutes.delay_task))
async def delay_progress(callback: CallbackQuery, callback_data: DTProgressActions, state: FSMContext):
    user_settings = await TgUserNotifierSettings.get_tg_user_settings(callback.from_user.id)
    delay_mins = user_settings.task_progress_delay_mins
    task_data = await pop_from_fsm_ctx_by_key(str(callback_data.task_id), state)
    task = DTProgressSchema(**task_data)
    notify_dt = datetime.now() + timedelta(minutes=delay_mins)
    if callback_data.event == DTaskNotifyEventTypes.start_dialog:
        if notify_dt >= task.end_dt:
            await callback.message.answer(
                text="Next notification time is greater than planned task end\n"
                     "We'll mark this task as failed\n"
                     "Copy it to some other datetime or delete if you want",
                reply_markup=task_control_kb(task.id),
            )
            TgDTaskNotifier.delete_dt_jobs(task.id)
    elif callback_data.event == DTaskNotifyEventTypes.end_dialog:
        if notify_dt > datetime.combine(task.end_dt.date(), time.max):
            await callback.message.answer(
                text="Day ended, we'll mark this task as failed\n"
                     "Copy it to some other datetime or delete if you want",
                reply_markup=task_control_kb(task.id),
            )
    else:
        await callback.message.answer("hmm.. this button works with created or started task states only")
        return
    TgDTaskNotifier.reschedule_event(callback.from_user.id, task, callback_data.event, notify_dt)
    await callback.message.answer(f"ok, i'll comeback in {delay_mins} minutes")


@control_task_state_router.callback_query(DTProgressActions.filter(F.action == KbDTProgressRoutes.disapprove_task))
async def disapprove_progress(callback: CallbackQuery, callback_data: DTProgressActions, state: FSMContext):
    await pop_from_fsm_ctx_by_key(str(callback_data.task_id), state)
    await DailyTaskService.fail_task(callback_data.task_id)
    TgDTaskNotifier.delete_dt_jobs(callback_data.task_id)
    await callback.message.answer(
        text="we'll mark this task as failed.\nCopy it to some other datetime or delete if you want",
        reply_markup=task_control_kb(callback_data.task_id),
    )
