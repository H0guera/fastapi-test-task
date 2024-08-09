import datetime

from pydantic import BaseModel, BeforeValidator, ConfigDict, PlainSerializer
from typing_extensions import Annotated

CustomDate = Annotated[
    datetime.date,
    BeforeValidator(
        lambda date: (
            datetime.datetime.strptime(date, "%d-%m-%Y").date()
            if isinstance(date, str)
            else date
        ),
    ),
    PlainSerializer(lambda x: x.strftime("%d-%m-%Y")),
]


CustomTime = Annotated[
    datetime.time,
    PlainSerializer(lambda time: time.strftime("%H:%M")),
]


class OrderModelDTO(BaseModel):
    """
    DTO for orders models.

    It returned when accessing orders models from the API.
    """

    dog_name: str
    room_number: int
    date: CustomDate
    time: CustomTime

    model_config = ConfigDict(from_attributes=True)


class OrderModelInputDTO(BaseModel):
    """DTO for creating new orders model."""

    dog_name: str
    room_number: int
    date: CustomDate
    time: CustomTime

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "dog_name": "Barbos",
                    "room_number": 77,
                    "date": "15-08-2024",
                    "time": "07:30",
                },
            ],
        },
    }
