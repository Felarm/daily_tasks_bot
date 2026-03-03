from datetime import datetime

from pydantic import BaseModel


class NewDailyTaskSchema(BaseModel):
    user_id: int
    name: str
    description: str | None
    start_dt: datetime
    end_dt: datetime


class DTUnsavedSchema(BaseModel):
    name: str
    description: str | None
    start_dt: datetime
    end_dt: datetime


class DTBeginSchema(BaseModel):
    id: int
    start_dt: datetime
    end_dt: datetime
    state: str