from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import TIMESTAMP, func, inspect
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    def to_dict(self, exclude_none: bool = False) -> dict[str, Any]:
        """does not append NULL fields to result if exclude_none = True"""
        result = {}
        for column in inspect(self.__class__).columns:
            value = getattr(self, column.key)
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, UUID):
                value = str(value)
            if not exclude_none or value is not None:
                result[column.key] = value
        return result

