from datetime import time

from sqlalchemy import ForeignKey, Boolean, JSON, Time
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class UserNotifierSettings(Base):
    __tablename__ = "users_notifier_settings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    enable_all_notifications: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    mins_before_dt_start: Mapped[list] = mapped_column(MutableList.as_mutable(JSON), nullable=False, default=list)
    progress_dt_notifications_enabled: Mapped[bool] = mapped_column(Boolean, nullable=True)
    today_dt_list_notification_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    today_dt_completion_analyze_time: Mapped[time | None] = mapped_column(Time, nullable=True)
