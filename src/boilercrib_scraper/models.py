"""Models for the data"""

from datetime import datetime
from typing import Annotated, ClassVar

from pydantic import BaseModel, ConfigDict, Field


class Building(BaseModel):
    _id             : str | None = None
    name            : str | None = None
    acronym         : str | None = None
    address         : str | None = None
    latitude        : float | None = None
    longitude       : float | None = None
    image           : str | None = None
    buildingType    : str | None = None

    model_config = ConfigDict(extra='forbid')


class DinningCourt(Building):
    stableOptions       : list[str] | None = None
    acceptsSwipes       : bool | None = None
    busyHours           : list[str] | None = None
    acceptsDiningDollars: bool | None = None
    acceptsBoilerExpress: bool | None = None

    model_config = ConfigDict(extra='forbid')


class Events(BaseModel):
    _id         : str | None = None
    eventName   : str | None = None
    summary     : str | None = None
    content     : str | None = None
    userID      : str | None = None
    date        : datetime | None = None
    address     : str | None = None

    model_config = ConfigDict(extra='forbid')


class Room(BaseModel):
    # Does not currently distinguish between capacity per bedroom or capacity per room
    capacity        : int | None = None
    features        : list[str] | None = None
    cost            : float | None = None
    housingRate     : float | None = None
    isSharedBathroom: bool | None = None
    buildingId      : str | None = None

    # Fields that don't exist in the backend yet:
    # category: str | None
    # # Couldn't find any instance where period is not "Academic Year" 
    # period: str | None  
    # airConditioning: bool | None

    model_config = ConfigDict(extra='forbid')


class Housing(Building):
    rooms           : list[Room] | None = None
    pianoNum        : int | None = None
    kitchenNum      : int | None = None
    haveDinningCourt: bool | None = None
    haveBoilerMarket: bool | None = None
    studySpaceNum   : int | None = None

    model_config = ConfigDict(extra='forbid')


class Review(BaseModel):
    MIN_RATING: ClassVar[int] = 1
    MAX_RATING: ClassVar[int] = 10

    _id         : str | None = None
    userId      : str | None = None
    description : str | None = None
    createdAt   : datetime | None = None
    rating      : Annotated[int | None, Field(ge=MIN_RATING, le=MAX_RATING)] = None
    likeCount   : int | None = None
    dislikeCount: int | None = None
    flagged     : bool | None = None
    buildingId  : str | None = None

    model_config = ConfigDict(extra='forbid')


# Don't think we'll need this
# class User(BaseModel):
#     _id: str | None = None
#     username: str | None = None
#     password: str | None = None
#     name: str | None = None
#     phoneNumber: str | None = None
#     accountType: int | None = None
