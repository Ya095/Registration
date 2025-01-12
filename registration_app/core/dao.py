from typing import List, TypeVar, Generic
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import (
    update as sqlalchemy_update,
    delete as sqlalchemy_delete,
    func,
)
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from .models.base import Base


# Объявляем типовой параметр T с ограничением, что это наследник Base
T = TypeVar("T", bound=Base)


class BaseDAO(Generic[T]):
    model: type[T]

    @classmethod
    async def find_one_or_none_by_id(cls, data_id: int, session: AsyncSession) -> type[T]:
        """Найти запись по ID"""

        logger.info(f"Поиск {cls.model.__name__} с ID: {data_id}")
        try:
            query = select(cls.model).filter_by(id=data_id)
            result = await session.execute(query)
            record = result.scalar_one_or_none()
            if record:
                logger.info(f"Запись с ID {data_id} найдена.")
            else:
                logger.info(f"Запись с ID {data_id} не найдена.")
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи с ID {data_id}: {e}")
            raise

    @classmethod
    async def find_one_or_none(
        cls, session: AsyncSession, filters: BaseModel
    ) -> type[T]:
        """Найти одну запись по фильтрам"""

        filter_dict = filters.model_dump(exclude_unset=True)
        logger.info(
            f"Поиск одной записи {cls.model.__name__} по фильтрам: {filter_dict}"
        )
        try:
            query = select(cls.model).filter_by(**filter_dict)
            result = await session.execute(query)
            record: type[T] = result.scalar_one_or_none()

            if record:
                logger.info(f"Запись найдена по фильтрам: {filter_dict}")
            else:
                logger.info(f"Запись не найдена по фильтрам: {filter_dict}")
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи по фильтрам {filter_dict}: {e}")
            raise

    @classmethod
    async def find_all(cls, session: AsyncSession, filters: BaseModel | None):
        """Найти все записи по фильтрам или без них"""

        if filters:
            filter_dict = filters.model_dump(exclude_unset=True)
        else:
            filter_dict = {}
        logger.info(
            f"Поиск всех записей {cls.model.__name__} по фильтрам: {filter_dict}"
        )
        try:
            query = select(cls.model).filter_by(**filter_dict)
            result = await session.execute(query)
            records = result.scalars().all()
            logger.info(f"Найдено {len(records)} записей.")
            return records
        except SQLAlchemyError as e:
            logger.error(
                f"Ошибка при поиске всех записей по фильтрам {filter_dict}: {e}"
            )
            raise

    @classmethod
    async def add(cls, session: AsyncSession, values: BaseModel):
        """Добавить одну запись"""

        values_dict = values.model_dump(exclude_unset=True)
        logger.info(
            f"Добавление записи {cls.model.__name__} с параметрами: {values_dict}"
        )
        new_instance = cls.model(**values_dict)
        try:
            session.add(new_instance)
            await session.flush()
            # await session.commit()
            logger.info(f"Запись {cls.model.__name__} успешно добавлена.")
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Ошибка при добавлении записи: {e}")
            raise e
        return new_instance

    @classmethod
    async def add_many(cls, session: AsyncSession, instances: List[BaseModel]):
        """Добавить несколько записей"""

        values_list = [item.model_dump(exclude_unset=True) for item in instances]
        logger.info(f"Добавление нескольких записей {cls.model.__name__}. Количество: {len(values_list)}")
        new_instances = [cls.model(**values) for values in values_list]
        session.add_all(new_instances)
        try:
            await session.flush()
            # await session.commit()
            logger.info(f"Успешно добавлено {len(new_instances)} записей.")
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Ошибка при добавлении нескольких записей {cls.model.__name__}: {e}")
            raise e
        return new_instances

    @classmethod
    async def update(cls, session: AsyncSession, filters: BaseModel, values: BaseModel):
        """Обновить записи по фильтрам"""

        filter_dict = filters.model_dump(exclude_unset=True)
        values_dict = values.model_dump(exclude_unset=True)
        logger.info(
            f"Обновление записей {cls.model.__name__} по фильтру: {filter_dict} "
            f"с параметрами: {values_dict}"
        )
        query = (
            sqlalchemy_update(cls.model)
            .where(*[getattr(cls.model, k) == v for k, v in filter_dict.items()])
            .values(**values_dict)
            .execution_options(synchronize_session="fetch")
        )
        try:
            result = await session.execute(query)
            await session.flush()
            # await session.commit()
            logger.info(f"Обновлено записей: {result.rowcount}")
            # return result.rowcount
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Ошибка при обновлении записей: {e}")
            raise e

    @classmethod
    async def delete(cls, session: AsyncSession, filters: BaseModel):
        """Удалить записи по фильтру"""

        filter_dict = filters.model_dump(exclude_unset=True)
        logger.info(
            f"Удаление записей модели {cls.model.__name__} "
            f"по фильтру: {filter_dict}"
        )
        if not filter_dict:
            logger.error("Нужен хотя бы один фильтр для удаления.")
            raise ValueError("Нужен хотя бы один фильтр для удаления.")

        query = sqlalchemy_delete(cls.model).filter_by(**filter_dict)
        try:
            result = await session.execute(query)
            await session.flush()
            # await session.commit()
            logger.info(f"Удалено {result.rowcount} записей.")
            # return result.rowcount
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Ошибка при удалении записей: {e}")
            raise e

    @classmethod
    async def count(cls, session: AsyncSession, filters: BaseModel):
        """Подсчитать количество записей"""

        filter_dict = filters.model_dump(exclude_unset=True)
        logger.info(
            f"Подсчет количества записей модели {cls.model.__name__} "
            f"по фильтру: {filter_dict}"
        )
        try:
            query = select(func.count(cls.model.id)).filter_by(**filter_dict)
            result = await session.execute(query)
            count = result.scalar()
            logger.info(f"Найдено {count} записей.")
            return count
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при подсчете записей: {e}")
            raise

    @classmethod
    async def paginate(
        cls,
        session: AsyncSession,
        page: int = 1,
        page_size: int = 10,
        filters: BaseModel = None,
    ):
        """Пагинация записей"""

        filter_dict = filters.model_dump(exclude_unset=True) if filters else {}
        logger.info(
            f"Пагинация записей модели {cls.model.__name__} по фильтру: {filter_dict}, "
            f"страница: {page}, размер страницы: {page_size}"
        )
        try:
            query = select(cls.model).filter_by(**filter_dict)
            result = await session.execute(
                query.offset((page - 1) * page_size).limit(page_size)
            )
            records = result.scalars().all()
            logger.info(f"Найдено {len(records)} записей на странице {page}.")
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при пагинации записей: {e}")
            raise

    @classmethod
    async def upsert(
        cls, session: AsyncSession, unique_fields: List[str], values: BaseModel
    ):
        """Создать запись или обновить существующую"""

        values_dict = values.model_dump(exclude_unset=True)
        filter_dict = {
            field: values_dict[field] for field in unique_fields if field in values_dict
        }

        logger.info(f"Upsert для {cls.model.__name__}")
        try:
            existing = await cls.find_one_or_none(
                session, BaseModel.model_construct(**filter_dict)
            )
            if existing:
                # Обновляем существующую запись
                for key, value in values_dict.items():
                    setattr(existing, key, value)
                await session.flush()
                # await session.commit()
                logger.info(f"Обновлена существующая запись {cls.model.__name__}")
                return existing
            else:
                # Создаем новую запись
                new_instance = cls.model(**values_dict)
                session.add(new_instance)
                await session.flush()
                # await session.commit()
                logger.info(f"Создана новая запись {cls.model.__name__}")
                return new_instance
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Ошибка при upsert: {e}")
            raise

    @classmethod
    async def make_inactive(cls, session: AsyncSession, filters: BaseModel):
        """Сделать неактивными записи (is_active=False) по фильтрам"""

        filter_dict = filters.model_dump(exclude_unset=True)
        logger.info(
            f"Деактивация записей модели {cls.model.__name__} по фильтру: {filter_dict}"
        )
        if not filter_dict:
            logger.error("Нужен хотя бы один фильтр для деактивации.")
            raise ValueError("Нужен хотя бы один фильтр для деактивации.")

        query = (
            sqlalchemy_update(cls.model)
            .where(*[getattr(cls.model, k) == v for k, v in filter_dict.items()])
            .values(is_active=False)
            .execution_options(synchronize_session="fetch")
        )
        try:
            result = await session.execute(query)
            await session.flush()
            # await session.commit()
            logger.info(f"Деактивировано записей: {result.rowcount}")
            # return result.rowcount
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Ошибка при деактивации записей: {e}")
            raise e

    @classmethod
    async def make_inactive_by_id(cls, session: AsyncSession, data_id: int):
        """Сделать неактивной запись (is_active=False) по id"""

        logger.info(
            f"Деактивация записи модели {cls.model.__name__} с id {data_id}"
        )
        if not data_id:
            logger.error("Не передан id для деактивации.")
            raise ValueError("Не передан id для деактивации.")

        query = (
            sqlalchemy_update(cls.model)
            .where(getattr(cls.model, "id") == data_id)  # type: ignore
            .values(is_active=False)
            .execution_options(synchronize_session="fetch")
        )
        try:
            await session.execute(query)
            await session.flush()
            # await session.commit()
            logger.info(f"Запись деактивирована (id {data_id})")
            # return result.rowcount
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Ошибка при деактивации записи {cls.model.__name__} id {data_id}")
            raise e
