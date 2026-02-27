from pydantic import BaseModel


class NewUserSchema(BaseModel):
    id_: int
    username: str
    first_name: str | None
    last_name: str | None
    language_code: str | None