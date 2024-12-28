from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy import MetaData
from core.config import settings
from core.utils.case_converter import camel_case_to_snake_case


class Base(DeclarativeBase):
    __abstract__ = True

    metadata = MetaData(
        naming_convention=settings.db.naming_convention
    )

    @declared_attr
    def __tablename__(cls) -> str:
        return f"{camel_case_to_snake_case(cls.__name__)}s"
