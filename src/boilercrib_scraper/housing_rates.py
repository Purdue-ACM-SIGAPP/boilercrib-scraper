import datetime as dt
import logging
from collections.abc import Generator
from csv import DictReader

from boilercrib_scraper.matching import Matcher
from boilercrib_scraper.models import Room

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class HousingRatesRow:
    def __init__(self, row_dict: dict[str, str]):
        """Construct a HousingRatesRowObject.

        Raises:
            KeyError: If the CSV columns are different than expected.
        """
        self.room_type_id = row_dict["Room Type ID"]
        self.room_type = row_dict["Room Type"]
        self.term = row_dict["Term"]
        self.housing_type = row_dict["Housing Type"]
        self.category = row_dict["Category"]
        self.period = row_dict["Period"]
        self.amount = row_dict["Amount"]
        self.term_description = row_dict["Term Description"]
        self.building = row_dict["Building"]
        self.location = row_dict["Location"]
        self.ur_boiler_apartment = row_dict["UR Boiler Apartment"]
        self.capacity = row_dict["Capacity"]
        self.air_conditioning = row_dict["Air Conditioning"]
        self.bath = row_dict["Bath"]
        self.pk = row_dict["PK"]


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
        row = HousingRatesRow(row_dict)

        # Filter by starting year
        # TODO test
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
        if row.location != location:
            logger.debug(f"Row {i}: location {row.location} != {location}, skipping.")
            continue

        # Get building id
        matches = matcher.match(row.building)
        if len(matches) > 2:
            logger.warning(
                f"Row {i}: Multiple matches for '{row.building}', going with first: {matches}"
            )
        elif len(matches) == 0:
            logger.warning(
                f"Row {i}: Did not find a match for '{row.building}', skipping."
            )
            continue
        building_id = matches[0].id

        # Parse capacity
        parse_capacity_result = _parse_capacity(row.capacity)
        if parse_capacity_result is None:
            logger.error(
                f"Row {i}: Failed to parse capacity '{row.capacity}', skipping."
            )
            continue  # Maybe this should raise an exception instead of continuing
        capacity_range_start, capacity_range_end, capacity_per = parse_capacity_result

        category = row.category

        try:
            housing_rate = float(row.amount)
        except ValueError as e:
            logger.error(f"Row {i}: Failed to parse housing rate: {e}. skipping.")
            continue  # Maybe this should raise an exception instead of continuing

        period = row.period

        assert row.air_conditioning in ("TRUE", "FALSE")
        is_air_conditioned = row.air_conditioning == "TRUE"

        yield Room(
            capacityRangeStart=capacity_range_start,
            capacityRangeEnd=capacity_range_end,
            capacityPer=capacity_per,
            category=category,
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
