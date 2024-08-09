from datetime import datetime

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from test_project_fastapi.db.dao.order_dao import OrderDAO
from test_project_fastapi.settings import settings


# Creation
@pytest.mark.freeze_time("2024-08-09 08:30:40+3:00")
@pytest.mark.anyio
async def test_creation(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:

    dao = OrderDAO(dbsession)
    instances = await dao.get_all_dummies(offset=0)

    url = fastapi_app.url_path_for("create_order_model")
    response = await client.put(
        url,
        json={
            "dog_name": "barbos",
            "room_number": 55,
            "date": "10-08-2024",
            "time": "08:30",
        },
    )
    instances_after_creation = await dao.get_all_dummies(offset=0)

    assert response.status_code == status.HTTP_200_OK
    assert len(instances) < len(instances_after_creation)
    assert instances_after_creation[-1].dog_name == "barbos"
    assert instances_after_creation[-1].room_number == 55


@pytest.mark.freeze_time("2024-08-09 08:30:40+3:00")
@pytest.mark.anyio
async def test_422_limit_performers(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:

    payload = {
        "dog_name": "barbos",
        "room_number": 55,
        "date": "10-08-2024",
        "time": "07:00",
    }
    url = fastapi_app.url_path_for("create_order_model")

    for _ in range(settings.performers):
        response = await client.put(
            url,
            json=payload,
        )
        assert response.status_code == status.HTTP_200_OK
    target_response = await client.put(
        url,
        json=payload,
    )

    assert target_response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.freeze_time("2024-08-09 08:30:40+3:00")
@pytest.mark.anyio
async def test_422_wrong_time(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:

    url = fastapi_app.url_path_for("create_order_model")
    wrong_times = ["06:30", "05:00", "23:30", "07:25", "07:300", "24:00", "7:30"]

    for time in wrong_times:
        response = await client.put(
            url,
            json={
                "dog_name": "barbos",
                "room_number": 55,
                "date": "10-08-2024",
                "time": time,
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.freeze_time("2024-08-09 08:30:40+3:00")
@pytest.mark.anyio
async def test_422_past_date_time(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:

    url = fastapi_app.url_path_for("create_order_model")
    response_from_past_date = await client.put(
        url,
        json={
            "dog_name": "barbos",
            "room_number": 55,
            "date": "08-08-2024",
            "time": "07:00",
        },
    )
    response_from_past_time = await client.put(
        url,
        json={
            "dog_name": "barbos",
            "room_number": 55,
            "date": "09-08-2024",
            "time": "07:00",
        },
    )
    assert response_from_past_date.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response_from_past_time.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response_from_past_date.text == '{"detail":"The time specified has passed"}'
    assert response_from_past_time.text == '{"detail":"The time specified has passed"}'


@pytest.mark.freeze_time("2024-08-09 08:30:40+3:00")
@pytest.mark.anyio
async def test_422_room_number_not_in_range(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:

    url = fastapi_app.url_path_for("create_order_model")
    response_from_past_date = await client.put(
        url,
        json={
            "dog_name": "barbos",
            "room_number": -1,
            "date": "10-08-2024",
            "time": "07:00",
        },
    )

    assert response_from_past_date.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# List
@pytest.mark.anyio
async def test_getting(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:

    dao = OrderDAO(dbsession)
    db_orders = await dao.get_all_dummies(offset=0)
    url = fastapi_app.url_path_for("get_order_models")
    response = await client.get(url)
    orders = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(orders) == len(db_orders)


@pytest.mark.anyio
async def test_getting_with_date_param(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:

    dao = OrderDAO(dbsession)
    date_str = "15-08-2024"
    date = datetime.strptime(date_str, "%d-%m-%Y").date()
    param = {"date": date_str}
    db_orders = await dao.get_all_dummies(offset=0, date=date)
    url = fastapi_app.url_path_for("get_order_models")
    response = await client.get(url, params=param)
    orders = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(orders) == len(db_orders)
