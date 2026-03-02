import enum
from datetime import datetime
from typing import Any

from sqlalchemy import CheckConstraint, String, ForeignKey, DateTime, Enum, Integer, JSON, text
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base
from db.schemas import NotifySettingsSchema


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(255), unique=True)
    id: Mapped[int] = mapped_column(Integer, unique=True, primary_key=True, autoincrement=False)
    first_name: Mapped[str | None] = mapped_column(String(255))
    last_name: Mapped[str | None] = mapped_column(String(255))
    language_code: Mapped[str | None] = mapped_column(String(100))
    notify_settings: Mapped[dict[str, Any]] = mapped_column(
        JSON, default=lambda: NotifySettingsSchema().model_dump(),
    )


class DTaskState(enum.Enum):
    created = "created"
    in_progres = "in_progres"
    done = "done"
    failed = "failed"


class DailyTask(Base):
    __tablename__ = "daily_tasks"
    __table_args__ = (
        CheckConstraint(
            "start_dt < end_dt",
            name="time_period"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(String)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    start_dt: Mapped[datetime] = mapped_column(DateTime)
    end_dt: Mapped[datetime] = mapped_column(DateTime)
    state: Mapped[DTaskState] = mapped_column(Enum(DTaskState), default=DTaskState.created)
    real_start_dt: Mapped[datetime | None] = mapped_column(DateTime)
    real_end_dt: Mapped[datetime | None] = mapped_column(DateTime)
