from pydantic import BaseModel


class UserNotifierDailyTaskDataSchema(BaseModel):
    id: int
    name: str
    description: str
    start_dt: str
    end_dt: str
    user_id: int