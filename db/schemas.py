from pydantic import BaseModel, Field


class NotifySettingsSchema(BaseModel):
    enabled: bool
    mins_before_dt_start: list[int]

