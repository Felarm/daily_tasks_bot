from typing import Any

from pydantic import BaseModel
from sqlalchemy import String, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    tg_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notify_settings: Mapped[dict[str, Any]] = mapped_column(
        JSON, default=lambda: NotifySettingsSchema(enabled=True, mins_before_dt_start=[5]).model_dump(),
    )


class NotifySettingsSchema(BaseModel):
    enabled: bool
    mins_before_dt_start: list[int]

