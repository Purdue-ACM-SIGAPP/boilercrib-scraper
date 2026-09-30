"""Models for the data"""

from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel


class Building(BaseModel):
    _id             : str | None
    name            : str | None
    acronym         : str | None
    address         : str | None
    latitude        : float | None
    longitude       : float | None
    image           : str | None
    buildingType    : str | None


class DinningCourt(Building):
    stableOptions       : list[str] | None
    acceptsSwipes       : bool | None
    busyHours           : list[str] | None
    acceptsDiningDollars: bool | None
    acceptsBoilerExpress: bool | None


class Events(BaseModel):
    _id         : str | None
    eventName   : str | None
    summary     : str | None
    content     : str | None
    userID      : str | None
    date        : datetime | None
    address     : str | None


class Room(BaseModel):
    # Does not currently distinguish between capacity per bedroom or capacity per room
    capacity        : int | None
    features        : list[str] | None
    cost            : float | None
    housingRate     : float | None
    isSharedBathroom: bool | None
    buildingId      : str | None

    # Fields that don't exist in the backend yet:
    # category: str | None
    # # Couldn't find any instance where period is not "Academic Year" 
    # period: str | None  
    # airConditioning: bool | None


class Housing(Building):
    rooms           : list[Room] | None
    pianoNum        : int | None
    kitchenNum      : int | None
    haveDinningCourt: bool | None
    haveBoilerMarket: bool | None
    studySpaceNum   : int | None


class Review(BaseModel):
    MIN_RATING: ClassVar[int] = 1
    MAX_RATING: ClassVar[int] = 10

    _id         : str | None
    userId      : str | None
    description : str | None
    createdAt   : datetime | None
    rating      : int | None
    likeCount   : int | None
    dislikeCount: int | None
    flagged     : bool | None
    buildingId  : str | None


# Don't think we'll need this
# class User(BaseModel):
#     _id: str | None
#     username: str | None
#     password: str | None
#     name: str | None
#     phoneNumber: str | None
#     accountType: int | None
