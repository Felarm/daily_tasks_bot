from datetime import datetime

from pydantic import BaseModel


class DTUnsavedSchema(BaseModel):
    tg_user_id: int
    name: str
    description: str | None
    start_dt: datetime
    end_dt: datetime


class DTPreviewSchema(BaseModel):
    name: str
    description: str | None
    start_dt: datetime
    end_dt: datetime


class DTProgressSchema(BaseModel):
    id: int
    start_dt: datetime
    end_dt: datetime
    state: str