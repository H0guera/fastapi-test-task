import datetime
from typing import List

from fastapi import APIRouter
from fastapi.param_functions import Depends

from test_project_fastapi.db.dao.order_dao import OrderDAO
from test_project_fastapi.db.models.order_model import Order
from test_project_fastapi.web.api.orders.schema import (
    OrderModelDTO,
    OrderModelInputDTO,
)

router = APIRouter()


@router.get("/", response_model=List[OrderModelDTO])
async def get_order_models(
    limit: int | None = None,
    offset: int = 0,
    date: str | None = None,
    order_dao: OrderDAO = Depends(),
) -> List[Order]:
    """
    Retrieve all orders objects from the database.

    :param limit: limit of orders objects, defaults to None.
    :param offset: offset of orders objects, defaults to 0.
    :param date: date of orders objects in format "%d-%m-%Y", defaults to None.
    :param order_dao: DAO for orders models.
    :return: list of orders objects from database.
    """

    if date:
        date = datetime.datetime.strptime(date, "%d-%m-%Y").date()
    return await order_dao.get_all_dummies(limit=limit, offset=offset, date=date)


@router.put("/")
async def create_order_model(
    new_order_object: OrderModelInputDTO,
    order_dao: OrderDAO = Depends(),
) -> None:
    """
    Creates orders model in the database.

    :param dog_name: name of dog in str.
    :param room_number: number of your room in int.
    :param date: date in format "%d-%-m-%Y".
    :param time: time in format like "17:30" or "17:00" in range from 7:00 to 23:00".
    """
    await order_dao.create_order_model(order_dto=new_order_object)
