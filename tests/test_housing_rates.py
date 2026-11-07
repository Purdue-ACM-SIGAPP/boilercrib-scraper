from pathlib import Path

import pytest

from boilercrib_scraper.housing_rates import get_housing_rates
from boilercrib_scraper.matching import SEED_PATH, load_seed
from boilercrib_scraper.models import Room

ROOM_RATES_27_28_CSV_PATH = (
    Path(__file__).parent / "fixtures" / "housing_rates" / "room-rates2728.csv"
)
ROOM_RATES_27_28_CSV = ROOM_RATES_27_28_CSV_PATH.read_text()

SEED_BUILDINGS = load_seed(SEED_PATH)
WINDSOR_ID = next(x for x in SEED_BUILDINGS if x.acronym == "WIND").id
WINIFRED_PARKER_ID = next(x for x in SEED_BUILDINGS if x.acronym == "PKRW").id
MCCUTCHEON_ID = next(x for x in SEED_BUILDINGS if x.acronym == "MCUT").id


@pytest.fixture(scope="module")
def housing_rates_27_28() -> list[Room]:
    return get_housing_rates(ROOM_RATES_27_28_CSV, 2027)


@pytest.mark.parametrize(
    "room",
    [
        # First room in 2027-28
        Room(
            capacityRangeStart=1,
            capacityRangeEnd=1,
            capacityPer="Bedroom",
            category="1 BR Apt",
            features=None,
            housingRate=18786,
            period="Academic Year",
            isSharedBathroom=None,
            isAirConditioned=True,
            buildingId=None,  # 3rd and West is not in the seed data as of 2026-11-07
        ),
        Room(
            capacityRangeStart=2,
            capacityRangeEnd=2,
            capacityPer="Room",
            category="Traditional - Double",
            features=None,
            housingRate=6128,
            period="Academic Year",
            isSharedBathroom=None,
            isAirConditioned=True,
            buildingId=WINDSOR_ID,
        ),
        # Last room in 2027-28
        Room(
            capacityRangeStart=2,
            capacityRangeEnd=2,
            capacityPer="Bedrooom",
            category="Full Suite - Double",
            features=None,
            housingRate=8250,
            period="Academic Year",
            isSharedBathroom=None,
            isAirConditioned=True,
            buildingId=WINIFRED_PARKER_ID,
        ),
    ],
)
def test_includes_correct_rooms(housing_rates_27_28: list[Room], room: Room):
    assert room in housing_rates_27_28


def test_capacity_range():
    # In the 2027-2028 CSV, the only entries that have a range are those for 2026-2027
    housing_rates_26_27 = get_housing_rates(ROOM_RATES_27_28_CSV, 2026)
    room = Room(
        capacityRangeStart=6,
        capacityRangeEnd=8,
        capacityPer="Room",
        category="Traditional - Quad",
        features=None,
        housingRate=4930,
        period="Academic Year",
        isSharedBathroom=None,
        isAirConditioned=True,
        buildingId=MCCUTCHEON_ID,
    )
    assert room in housing_rates_26_27
