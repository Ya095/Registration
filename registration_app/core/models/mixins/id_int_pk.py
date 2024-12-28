from sqlalchemy.orm import Mapped, mapped_column


class IdIntPkMixin:
    # Add id (pk) column to table
    id: Mapped[int] = mapped_column(primary_key=True)