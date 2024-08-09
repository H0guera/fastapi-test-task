from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import Date, Integer, String, Time

from test_project_fastapi.db.base import Base


class Order(Base):
    """Model for orders."""

    __tablename__ = "order_model"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    dog_name: Mapped[str] = mapped_column(String(length=200), nullable=False)
    room_number: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    time: Mapped[datetime.time] = mapped_column(Time, nullable=False)
