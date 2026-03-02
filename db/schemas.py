from pydantic import BaseModel, Field


class NotifySettingsSchema(BaseModel):
    enabled: bool = Field(default=True)
    mins_before_dt_start: list[int] = Field(default=[5])
