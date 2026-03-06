import enum
from datetime import datetime

from sqlalchemy import CheckConstraint, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


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
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    start_dt: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_dt: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    state: Mapped[DTaskState] = mapped_column(Enum(DTaskState), default=DTaskState.created, nullable=False)
    real_start_dt: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    real_end_dt: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
