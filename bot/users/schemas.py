from pydantic import BaseModel


class NewUserSchema(BaseModel):
    tg_id: int
    username: str
    first_name: str | None
    last_name: str | None
