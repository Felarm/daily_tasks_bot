from datetime import datetime

from aiogram_dialog import DialogManager

from bot.daily_tasks.schemas import DTPreviewSchema


async def get_confirmed_new_task_info(dialog_manager: DialogManager, **kwargs) -> dict[str, str]:
    task_model = DTPreviewSchema(**dialog_manager.dialog_data)
    confirm_text = (f"so... here is what you planned:\n"
                    f"<b>task name:</b> {task_model.name}\n"
                    f"<b>its description:</b> {task_model.description}\n"
                    f"<b>it should begin at:</b> {task_model.start_dt.isoformat(' ')}\n"
                    f"<b>and end by:</b> {task_model.end_dt.isoformat(' ')}\n\n"
                    f"we will notify you about its start 5 minutes before it starts\n"
                    f"be ready, darling...\n")
    return {"confirm_text": confirm_text}



async def get_confirmed_copy_task_info(dialog_manager: DialogManager, **kwargs) -> dict[str, str]:
    task_to_copy_data = DTPreviewSchema(**dialog_manager.start_data["task_to_copy"])
    orig_task_duration = task_to_copy_data.end_dt - task_to_copy_data.start_dt
    new_start_dt: datetime = dialog_manager.dialog_data["start_dt"]
    new_end_dt = new_start_dt + orig_task_duration
    confirm_text = (f"ok, we are going to make a copy of:\n"
                    f"<b>task name</b>: {task_to_copy_data.name}\n"
                    f"<b>new planned start</b>: {new_start_dt.isoformat(' ')}\n"
                    f"<b>new planned end</b>: {new_end_dt.isoformat(' ')}")
    return {"confirm_text": confirm_text}