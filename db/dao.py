from typing import TypeVar, Generic, Type

from loguru import logger
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import Base


T = TypeVar("T", bound=Base)


class BaseDao(Generic[T]):
    model: Type[T] = None

    def __init__(self, session: AsyncSession):
        self._session = session
        if self.model is None:
            raise ValueError("No model passed")

    async def get_one_or_none_by_id(self, id_: int) -> T | None:
        try:
            result = await self._session.get_one(self.model, id_)
            return result
        except NoResultFound:
            logger.error(f"Not found record for {self.model.__name__} with id: {id_}")
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error occured when looking record for {self.model.__name__} with id {id_}:\n{e}")
            raise
