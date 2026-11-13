from pathlib import Path

import pytest

from boilercrib_scraper.housing_rates import (
    HousingRatesRow,
    _get_room_from_row,
    _get_starting_year_from_term,
    _parse_capacity,
    get_rooms_from_housing_rates_csv,
)
from boilercrib_scraper.matching import Matcher
from boilercrib_scraper.models import Room

ROOM_RATES_27_28_CSV_PATH = (
    Path(__file__).parent / "fixtures" / "housing_rates" / "room-rates2728.csv"
)
ROOM_RATES_27_28_CSV = ROOM_RATES_27_28_CSV_PATH.read_text()


@pytest.fixture(scope="module")
def housing_rates_27_28() -> list[Room]:
    return list(get_rooms_from_housing_rates_csv(ROOM_RATES_27_28_CSV, 2027))


@pytest.fixture(scope="module")
def matcher() -> Matcher:
    return Matcher()


@pytest.fixture(scope="module")
def windsor_id(matcher: Matcher) -> str:
    return matcher.match("Windsor")[0].id


@pytest.fixture(scope="module")
def winifred_parker_id(matcher: Matcher) -> str:
    return matcher.match("Winifred Parker")[0].id


@pytest.fixture(scope="module")
def mccutcheon_id(matcher: Matcher) -> str:
    return matcher.match("McCutcheon")[0].id


def test_row_from_str():
    row = HousingRatesRow.from_str(
        "75,Suite w/shrd bath,2027-28,Undergraduate Housing,Full Suite - Double,Academic Year,8250,Academic Year 2027-28,Winifred Parker Hall,West Lafayette,FALSE,2/Bedroom,TRUE,TRUE,Suite w/shrd bathWinifred Parker Hall2027-28"
    )
    expected = HousingRatesRow(
        room_type_id="75",
        room_type="Suite w/shrd bath",
        term="2027-28",
        housing_type="Undergraduate Housing",
        category="Full Suite - Double",
        period="Academic Year",
        amount="8250",
        term_description="Academic Year 2027-28",
        building="Winifred Parker Hall",
        location="West Lafayette",
        ur_boiler_apartment="FALSE",
        capacity="2/Bedroom",
        air_conditioning="TRUE",
        bath="TRUE",
        pk="Suite w/shrd bathWinifred Parker Hall2027-28",
    )
    assert row == expected


def test_get_windsor_room_from_row(matcher: Matcher, windsor_id: str):
    row = HousingRatesRow.from_str(
        "4,Double w/priv bath,2027-28,Undergraduate Housing,Traditional - Double,Academic Year,6128,Academic Year 2027-28,Windsor Halls,West Lafayette,FALSE,2/Room,TRUE,TRUE,Double w/priv bathWindsor Halls2027-28"
    )
    expected = Room(
        capacityRangeStart=2,
        capacityRangeEnd=2,
        capacityPer="Room",
        roomType="Double w/priv bath",
        features=None,
        housingRate=6128,
        period="Academic Year",
        isSharedBathroom=None,
        isAirConditioned=True,
        buildingId=windsor_id,
    )
    assert _get_room_from_row(row, matcher) == expected


def test_get_winifred_parker_room_from_row(matcher: Matcher, winifred_parker_id: str):
    row = HousingRatesRow.from_str(
        "75,Suite w/shrd bath,2027-28,Undergraduate Housing,Full Suite - Double,Academic Year,8250,Academic Year 2027-28,Winifred Parker Hall,West Lafayette,FALSE,2/Bedroom,TRUE,TRUE,Suite w/shrd bathWinifred Parker Hall2027-28"
    )
    expected = Room(
        capacityRangeStart=2,
        capacityRangeEnd=2,
        capacityPer="Bedroom",
        roomType="Suite w/shrd bath",
        features=None,
        housingRate=8250,
        period="Academic Year",
        isSharedBathroom=None,
        isAirConditioned=True,
        buildingId=winifred_parker_id,
    )
    assert _get_room_from_row(row, matcher) == expected


def test_get_ranged_capacity_room_from_row(matcher: Matcher, mccutcheon_id: str):
    row = HousingRatesRow.from_str(
        # From the 2026-27 CSV
        "193,Quad Plus w/AC,2026-27,Undergraduate Housing,Traditional - Quad,Academic Year,4930,Academic Year 2026-27,McCutcheon Hall,West Lafayette,FALSE,6-8/Room,TRUE,FALSE"
    )
    expected = Room(
        capacityRangeStart=6,
        capacityRangeEnd=8,
        capacityPer="Room",
        roomType="Quad Plus w/AC",
        features=None,
        housingRate=4930,
        period="Academic Year",
        isSharedBathroom=None,
        isAirConditioned=True,
        buildingId=mccutcheon_id,
    )
    assert _get_room_from_row(row, matcher) == expected


@pytest.mark.parametrize("term,expected", [("2026-27", 2026), ("2027-28", 2027)])
def test_get_starting_year_from_term_field(term: str, expected: int):
    assert _get_starting_year_from_term(term) == expected


@pytest.mark.parametrize(
    "capacity_str,expected",
    [
        ("2", (2, 2, None)),
        ("4", (4, 4, None)),
        ("1/Bedroom", (1, 1, "Bedroom")),
        ("3/Room", (3, 3, "Room")),
        ("5-8/Room", (5, 8, "Room")),
        ("6-8/Room", (6, 8, "Room")),
    ],
)
def test_parse_capacity_field(capacity_str: str, expected: tuple[int, int, str | None]):
    assert _parse_capacity(capacity_str) == expected


def test_get_rooms_from_housing_rates_csv_restricts_year(matcher: Matcher):
    csv = """Room Type ID,Room Type,Term,Housing Type,Category,Period,Amount,Term Description,Building,Location,UR Boiler Apartment,Capacity,Air Conditioning,Bath,PK
0,Housing 2026,2026-27,n/a,n/a,Academic Year,8250,Academic Year 2026-27,Winifred Parker Hall,West Lafayette,FALSE,2/Bedroom,TRUE,TRUE,Suite w/shrd bathWinifred Parker Hall2027-28
0,Housing 2027,2027-28,n/a,n/a,Academic Year,8250,Academic Year 2027-28,Winifred Parker Hall,West Lafayette,FALSE,2/Bedroom,TRUE,TRUE,Suite w/shrd bathWinifred Parker Hall2027-28
"""
    results_2027 = tuple(get_rooms_from_housing_rates_csv(csv, 2027, matcher=matcher))
    assert len(results_2027) == 1
    assert results_2027[0].roomType == "Housing 2027"
    results_2026 = tuple(get_rooms_from_housing_rates_csv(csv, 2026, matcher=matcher))
    assert len(results_2026) == 1
    assert results_2026[0].roomType == "Housing 2026"


def test_get_rooms_from_housing_rates_csv_restricts_location(matcher: Matcher):
    csv = """Room Type ID,Room Type,Term,Housing Type,Category,Period,Amount,Term Description,Building,Location,UR Boiler Apartment,Capacity,Air Conditioning,Bath,PK
0,Housing West Lafayette,2027-28,n/a,n/a,Academic Year,8250,Academic Year 2027-28,Winifred Parker Hall,West Lafayette,FALSE,2/Bedroom,TRUE,TRUE,Suite w/shrd bathWinifred Parker Hall2027-28
0,Housing Indiana,2027-28,n/a,n/a,Academic Year,8250,Academic Year 2027-28,Winifred Parker Hall,Indiana,FALSE,2/Bedroom,TRUE,TRUE,Suite w/shrd bathWinifred Parker Hall2027-28
"""
    results_wl = tuple(
        get_rooms_from_housing_rates_csv(csv, 2027, "West Lafayette", matcher)
    )
    assert len(results_wl) == 1
    assert results_wl[0].roomType == "Housing West Lafayette"
    results_in = tuple(get_rooms_from_housing_rates_csv(csv, 2027, "Indiana", matcher))
    assert len(results_in) == 1
    assert results_in[0].roomType == "Housing Indiana"
