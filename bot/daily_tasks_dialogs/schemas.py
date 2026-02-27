from datetime import datetime, date

from pydantic import BaseModel


class NewDailyTaskSchema(BaseModel):
    user_id: int
    name: str
    description: str | None
    start_dt: datetime
    end_dt: datetime


class DailyTaskInfoSchema(BaseModel):
    name: str
    description: str | None
    start_dt: datetime
    end_dt: datetime