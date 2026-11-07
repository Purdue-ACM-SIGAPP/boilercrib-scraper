"""Models for the data"""

from datetime import datetime
from typing import Annotated, ClassVar

from pydantic import BaseModel, ConfigDict, Field


class Building(BaseModel):
    id: str | None = None
    name: str | None = None
    acronym: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    image: str | None = None
    buildingType: str | None = None

    model_config = ConfigDict(extra="forbid")


class DinningCourt(Building):
    stableOptions: list[str] | None = None
    acceptsSwipes: bool | None = None
    busyHours: list[str] | None = None
    acceptsDiningDollars: bool | None = None
    acceptsBoilerExpress: bool | None = None

    model_config = ConfigDict(extra="forbid")


class Events(BaseModel):
    id: str | None = None
    eventName: str | None = None
    summary: str | None = None
    content: str | None = None
    userID: str | None = None
    date: datetime | None = None
    address: str | None = None

    model_config = ConfigDict(extra="forbid")


class Room(BaseModel):
    capacityRangeStart: int | None = None
    capacityRangeEnd: int | None = None
    capacityPer: str | None = None
    category: str | None = None
    features: list[str] | None = None
    housingRate: float | None = None
    period: str | None = None
    isSharedBathroom: bool | None = None
    isAirConditioned: bool | None = None
    buildingId: str | None = None

    model_config = ConfigDict(extra="forbid")


class Housing(Building):
    rooms: list[Room] | None = None
    pianoNum: int | None = None
    kitchenNum: int | None = None
    haveDinningCourt: bool | None = None
    haveBoilerMarket: bool | None = None
    studySpaceNum: int | None = None

    model_config = ConfigDict(extra="forbid")


class Review(BaseModel):
    MIN_RATING: ClassVar[int] = 1
    MAX_RATING: ClassVar[int] = 10

    id: str | None = None
    userId: str | None = None
    description: str | None = None
    createdAt: datetime | None = None
    rating: Annotated[int | None, Field(ge=MIN_RATING, le=MAX_RATING)] = None
    likeCount: int | None = None
    dislikeCount: int | None = None
    flagged: bool | None = None
    buildingId: str | None = None

    model_config = ConfigDict(extra="forbid")


# Don't think we'll need this
# class User(BaseModel):
#     id: str | None = None
#     username: str | None = None
#     password: str | None = None
#     name: str | None = None
#     phoneNumber: str | None = None
#     accountType: int | None = None
