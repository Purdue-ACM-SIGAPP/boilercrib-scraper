import datetime as dt
import logging
from collections.abc import Generator
from csv import DictReader
from dataclasses import dataclass
from enum import StrEnum

from boilercrib_scraper.matching import Matcher
from boilercrib_scraper.models import Room

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Fieldnames(StrEnum):
    ROOM_TYPE_ID = "Room Type ID"
    ROOM_TYPE = "Room Type"
    TERM = "Term"
    HOUSING_TYPE = "Housing Type"
    CATEGORY = "Category"
    PERIOD = "Period"
    AMOUNT = "Amount"
    TERM_DESCRIPTION = "Term Description"
    BUILDING = "Building"
    LOCATION = "Location"
    UR_BOILER_APARTMENT = "UR Boiler Apartment"
    CAPACITY = "Capacity"
    AIR_CONDITIONING = "Air Conditioning"
    BATH = "Bath"
    PK = "PK"


ORDERED_FIELDNAMES = (
    Fieldnames.ROOM_TYPE_ID,
    Fieldnames.ROOM_TYPE,
    Fieldnames.TERM,
    Fieldnames.HOUSING_TYPE,
    Fieldnames.CATEGORY,
    Fieldnames.PERIOD,
    Fieldnames.AMOUNT,
    Fieldnames.TERM_DESCRIPTION,
    Fieldnames.BUILDING,
    Fieldnames.LOCATION,
    Fieldnames.UR_BOILER_APARTMENT,
    Fieldnames.CAPACITY,
    Fieldnames.AIR_CONDITIONING,
    Fieldnames.BATH,
    Fieldnames.PK,
)


@dataclass
class HousingRatesRow:
    room_type_id: str
    room_type: str
    term: str
    housing_type: str
    category: str
    period: str
    amount: str
    term_description: str
    building: str
    location: str
    ur_boiler_apartment: str
    capacity: str
    air_conditioning: str
    bath: str
    pk: str

    @classmethod
    def from_dict(cls, row_dict) -> HousingRatesRow:
        """Construct a HousingRatesRow object.

        Raises:
            KeyError: If the CSV columns are different than expected.
        """
        return HousingRatesRow(
            room_type_id=row_dict[Fieldnames.ROOM_TYPE_ID],
            room_type=row_dict[Fieldnames.ROOM_TYPE],
            term=row_dict[Fieldnames.TERM],
            housing_type=row_dict[Fieldnames.HOUSING_TYPE],
            category=row_dict[Fieldnames.CATEGORY],
            period=row_dict[Fieldnames.PERIOD],
            amount=row_dict[Fieldnames.AMOUNT],
            term_description=row_dict[Fieldnames.TERM_DESCRIPTION],
            building=row_dict[Fieldnames.BUILDING],
            location=row_dict[Fieldnames.LOCATION],
            ur_boiler_apartment=row_dict[Fieldnames.UR_BOILER_APARTMENT],
            capacity=row_dict[Fieldnames.CAPACITY],
            air_conditioning=row_dict[Fieldnames.AIR_CONDITIONING],
            bath=row_dict[Fieldnames.BATH],
            pk=row_dict[Fieldnames.PK],
        )

    @classmethod
    def from_str(cls, row_str: str) -> HousingRatesRow:
        """Construct a HousingRatesRow object from a `str` row.

        Intended for testing. Prefer `from_dict()`.
        """
        dict_reader = DictReader([row_str], fieldnames=ORDERED_FIELDNAMES)
        row_dict = next(dict_reader)
        return HousingRatesRow.from_dict(row_dict)


class NoMatchError(Exception):
    """Raised when a building cannot be matched."""


def get_current_academic_year():
    est_zone = dt.timezone(dt.timedelta(hours=-5))
    today = dt.datetime.now(tz=est_zone)
    if today.month >= 8:
        return today.year
    else:
        return today.year - 1


def get_rooms_from_housing_rates_csv(
    csv_file: str,
    starting_year: int = get_current_academic_year(),
    location: str = "West Lafayette",
    matcher: Matcher | None = None,
) -> Generator[Room]:
    """Get `Room`s from a housing rates CSV file.

    Args:
        csv_file (str): The housing rates CSV file.
        starting_year (int): The first year of the academic year to get `Room`s from.
        location (str): The location to get `Room`s from.

    Returns:
        Generator[Room]: The rooms.

    Raises:
        KeyError: If the CSV columns are different than expected.
    """
    if matcher is None:
        matcher = Matcher()

    dict_reader = DictReader(csv_file.splitlines())
    for i, row_dict in enumerate(dict_reader):
        row = HousingRatesRow.from_dict(row_dict)

        # Filter by starting year
        row_starting_year = _get_starting_year_from_term(row.term)
        if row_starting_year is None:
            logger.error(
                f"Row {i}: Failed to get starting year from term '{row.term}', skipping."
            )
            continue  # Maybe this should raise an exception instead of continuing
        if row_starting_year != starting_year:
            logger.debug(
                f"Row {i}: starting year {row_starting_year} != {starting_year}, skipping."
            )
            continue

        # Filter by location
        # TODO test
        if row.location != location:
            logger.debug(f"Row {i}: location {row.location} != {location}, skipping.")
            continue

        try:
            yield _get_room_from_row(row, matcher)
        except ValueError as e:
            logger.error(f"Error parsing row {i}: {e}")
        except NoMatchError:
            logger.warning(f"Did not get a match for {row.building}, skipping.")


def _get_room_from_row(row: HousingRatesRow, matcher: Matcher) -> Room:
    """Get `Room` from a HousingRatesRow.

    Args:
        row (HousingRatesRow): The row.
        matcher (Matcher): A Matcher instance.

    Returns:
        Room: A room

    Raises:
        ValueError: If something cannot be parsed correctly.
        NoMatchError: If the matcher cannot find a match for the building.
    """

    # Get building id
    matches = matcher.match(row.building)
    if len(matches) > 2:
        logger.warning(
            f"Multiple matches for '{row.building}': {matches}, going with the first."
        )
    elif len(matches) == 0:
        raise NoMatchError

    building_id = matches[0].id

    # Parse capacity
    parse_capacity_result = _parse_capacity(row.capacity)
    if parse_capacity_result is None:
        raise ValueError(f"Failed to parse capacity '{row.capacity}'.")
    capacity_range_start, capacity_range_end, capacity_per = parse_capacity_result

    room_type = row.room_type

    try:
        housing_rate = float(row.amount)
    except ValueError as e:
        raise ValueError(f"Failed to parse housing rate: {e}. skipping.")

    period = row.period

    assert row.air_conditioning in ("TRUE", "FALSE")
    is_air_conditioned = row.air_conditioning == "TRUE"

    return Room(
        capacityRangeStart=capacity_range_start,
        capacityRangeEnd=capacity_range_end,
        capacityPer=capacity_per,
        roomType=room_type,
        features=None,
        housingRate=housing_rate,
        period=period,
        isSharedBathroom=None,
        isAirConditioned=is_air_conditioned,
        buildingId=building_id,
    )


def _get_starting_year_from_term(term: str) -> int | None:
    """Get the starting year of the academic year from the term field of the housing rates CSV.

    Args:
        term (str): The term field of an entry in the housing rates CSV.

    Returns:
        int | None:
            The starting year of the academic year described by `term`.
            Returns `None` if it could not be parsed.
    """
    starting_year_str = term[:4]
    if len(starting_year_str) != 4:
        return None
    try:
        return int(starting_year_str)
    except ValueError:
        return None


def _parse_capacity(capacity_str: str) -> tuple[int, int, str | None] | None:
    """Parse capacity from values of the capacity field of the housing rates CSV.

    Args:
        capacity_str (str): The capacity field of an entry in the housing rates CSV.

    Returns:
        tuple[int, int, str | None] | None:
            The start and end of the capacity range, and what the capacity is
            applied to, respectively.
            The last value is `None` if it cannot be found.
            Returns `None` if parsing failed.
    """
    if "/" in capacity_str:
        capacity_str, capacity_per = capacity_str.split("/")
        if capacity_per == "":
            capacity_per = None
    else:
        capacity_per = None  # Ambiguous based on the rows that lack this information

    if "-" in capacity_str:
        try:
            capacity_range_start, capacity_range_end = map(int, capacity_str.split("-"))
        except ValueError:
            return None
    else:
        try:
            capacity = int(capacity_str)
        except ValueError:
            return None

        capacity_range_start = capacity
        capacity_range_end = capacity

    return capacity_range_start, capacity_range_end, capacity_per
