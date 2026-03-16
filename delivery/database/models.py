import datetime
import typing
import uuid

import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class BaseServiceModel(DeclarativeBase):
    publishing_datetime: Mapped[datetime.datetime] = mapped_column(
        sqlalchemy.types.DateTime, server_default=sqlalchemy.text("CURRENT_DATE"), nullable=True
    )
    changed_by: Mapped[str | None]
    changed_at: Mapped[datetime.datetime] = mapped_column(
        sqlalchemy.types.DateTime, server_default=sqlalchemy.text("CURRENT_DATE"), nullable=True
    )
    is_deleted: Mapped[bool] = mapped_column(sqlalchemy.types.Boolean, default=False)

    def to_dict(self, exclude: set[str] | None = None) -> dict[str, typing.Any]:
        exclude = exclude or set()
        return {
            col.key: getattr(self, col.key)
            for col in sqlalchemy.inspect(self.__class__).mapper.column_attrs
            if col.key not in exclude
        }


class OrderModel(BaseServiceModel):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(sqlalchemy.types.Uuid, primary_key=True)
    location_x: Mapped[int]
    location_y: Mapped[int]
    volume: Mapped[int]
    status: Mapped[str]
    courier_id: Mapped[uuid.UUID | None] = mapped_column(sqlalchemy.types.Uuid, nullable=True)


class StoragePlaceModel(BaseServiceModel):
    __tablename__ = "storage_places"

    id: Mapped[uuid.UUID] = mapped_column(sqlalchemy.types.Uuid, primary_key=True)
    courier_id: Mapped[uuid.UUID] = mapped_column(
        sqlalchemy.types.Uuid,
        sqlalchemy.ForeignKey("couriers.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str]
    total_volume: Mapped[int]
    order_id: Mapped[uuid.UUID | None] = mapped_column(sqlalchemy.types.Uuid, nullable=True)


class CourierModel(BaseServiceModel):
    __tablename__ = "couriers"

    id: Mapped[uuid.UUID] = mapped_column(sqlalchemy.types.Uuid, primary_key=True)
    name: Mapped[str]
    speed: Mapped[int]
    location_x: Mapped[int]
    location_y: Mapped[int]
    storage_places: Mapped[list[StoragePlaceModel]] = relationship(
        StoragePlaceModel,
        lazy="selectin",
        cascade="all, delete-orphan",
        foreign_keys=[StoragePlaceModel.courier_id],
    )
