from typing import Any

from pydantic import BaseModel
from sqlalchemy import String, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(255), unique=True)
    id: Mapped[int] = mapped_column(Integer, unique=True, primary_key=True, autoincrement=False)
    first_name: Mapped[str | None] = mapped_column(String(255))
    last_name: Mapped[str | None] = mapped_column(String(255))
    language_code: Mapped[str | None] = mapped_column(String(100))
    notify_settings: Mapped[dict[str, Any]] = mapped_column(
        JSON, default=lambda: NotifySettingsSchema(enabled=True, mins_before_dt_start=[5]).model_dump(),
    )


class NotifySettingsSchema(BaseModel):
    enabled: bool
    mins_before_dt_start: list[int]

