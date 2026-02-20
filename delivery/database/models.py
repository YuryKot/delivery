import datetime

import sqlalchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseServiceModel(DeclarativeBase):
    publishing_datetime: Mapped[datetime.datetime] = mapped_column(
        sqlalchemy.types.DateTime, server_default=sqlalchemy.text("CURRENT_DATE"), nullable=True
    )
    changed_by: Mapped[str | None]
    changed_at: Mapped[datetime.datetime] = mapped_column(
        sqlalchemy.types.DateTime, server_default=sqlalchemy.text("CURRENT_DATE"), nullable=True
    )
    is_deleted: Mapped[bool] = mapped_column(sqlalchemy.types.Boolean, default=False)
