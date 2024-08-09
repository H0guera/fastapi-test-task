import re
from datetime import datetime, timedelta, timezone
from typing import List, Union, Optional

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from test_project_fastapi.db.dependencies import get_db_session
from test_project_fastapi.db.models.order_model import Order
from test_project_fastapi.settings import settings
from test_project_fastapi.web.api.orders.schema import OrderModelInputDTO


class OrderDAO:
    """Class for accessing orders table."""

    def __init__(
        self,
        session: AsyncSession = Depends(get_db_session),
    ) -> None:
        self.session = session
        self.time_pattern = re.compile("^23:00|(0[7-9]|[1][0-9]|2[0-2]):[03]0$")

    async def create_order_model(self, order_dto: OrderModelInputDTO) -> None:
        """
        Add single orders to session.

        :param order_dto: DTO of order.
        """

        await self.validate_order_creation(order_dto)

        self.session.add(
            Order(
                dog_name=order_dto.dog_name,
                room_number=order_dto.room_number,
                date=order_dto.date,
                time=order_dto.time,
            ),
        )

    async def get_all_dummies(
        self,
        offset: int,
        limit: int | None = None,
        date: Union[datetime.date, None] = None,
    ) -> List[Order]:
        """
        Get all orders models with date filtering and limit/offset pagination.

        :param limit: limit of orders.
        :param offset: offset of orders.
        :param date: date of orders.
        :return: stream of orders.
        """
        stmt = (
            select(Order).limit(limit).offset(offset)
            if limit
            else select(Order).offset(offset)
        )

        raw_dummies = await self.session.execute(
            stmt if not date else stmt.where(Order.date == date).order_by(Order.time),
        )

        return list(raw_dummies.scalars().fetchall())

    async def filter(self, name: Optional[str] = None) -> List[Order]:
        """
        Get specific orders model.

        :param name: name of orders instance.
        :return: orders models.
        """
        query = select(Order)
        if name:
            query = query.where(Order.dog_name == name)
        rows = await self.session.execute(query)
        return list(rows.scalars().fetchall())

    async def validate_order_creation(self, order_dto: OrderModelInputDTO) -> None:
        """
        Validating InputDTO of order for creation.

        :param order_dto: InputDTO of order.
        :return: None.
        """
        await self.validate_room_number_in_range(order_dto)
        await self.validate_time_range(order_dto)
        await self.validate_is_future_date_time(order_dto)
        await self.validate_time_is_free(order_dto)

    async def validate_time_is_free(self, order_dto: OrderModelInputDTO) -> None:
        """
        At the same time on a given day can be only count of orders
        depending on count of performers (by settings) .

        :param order_dto: InputDTO of order.
        :return: None.
        """
        stmt = select(Order).where(
            Order.date == order_dto.date, Order.time == order_dto.time,
        )
        orders_by_date_and_time = await self.session.scalars(stmt)
        if len(orders_by_date_and_time.all()) >= settings.performers:
            raise HTTPException(
                status_code=422,
                detail="The time specified has reserved",
            )

    async def validate_is_future_date_time(self, order_dto: OrderModelInputDTO) -> None:
        """
        The desired time can only be in the future.

        :param order_dto: InputDTO of order.
        :return: None.
        """
        offset = timezone(timedelta(hours=settings.time_offset))
        now = datetime.now(offset)
        if order_dto.date > now.date():
            return
        if order_dto.date == now.date() and order_dto.time > now.time():
            return
        raise HTTPException(status_code=422, detail="The time specified has passed")

    async def validate_time_range(self, order_dto: OrderModelInputDTO) -> None:
        """
        Validating time format.

        :param order_dto: InputDTO of order.
        :return: None.
        """
        str_time = order_dto.time.strftime("%H:%M")
        if re.match(self.time_pattern, str_time):
            return
        raise HTTPException(
            status_code=422,
            detail='Time should be in format "08:00" or "08:30" '
            "and in range 07:00 to 23:00",
        )

    async def validate_room_number_in_range(
        self, order_dto: OrderModelInputDTO,
    ) -> None:
        """
        The target room should be in available range of rooms.

        :param order_dto: InputDTO of order.
        :return: None.
        """
        if order_dto.room_number in settings.available_room_numbers:
            return
        raise HTTPException(
            status_code=422,
            detail=f"The room number should be in range from "
                   f"{settings.first_room_number} to {settings.last_room_number}",
        )
