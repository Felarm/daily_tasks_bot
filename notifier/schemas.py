from datetime import time

from pydantic import BaseModel


class UpdatedSettings(BaseModel):
    enable_all_notifications: bool | None
    mins_before_dt_start: list[int] | None
    progress_dt_notifications_enabled: bool | None
    today_dt_list_notification_time: time | None
    today_dt_completion_analyze_time: time | None
