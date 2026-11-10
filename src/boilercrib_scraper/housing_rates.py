import datetime as dt
import logging
from collections.abc import Generator
from csv import DictReader

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
    dict_reader = DictReader(csv_file.splitlines())
    for i, row_dict in enumerate(dict_reader):
        row = HousingRatesRow(row_dict)

        # Filter by starting year
        # TODO test
        row_starting_year = _get_starting_year_from_term(row.term)
        if row_starting_year is None:
            logger.error(f'Row {i}: Failed to get starting year from term "{row.term}"')
            continue  # Maybe this should raise an exception instead of continuing
        if row_starting_year != starting_year:
            logger.debug(
                f"Skipping row {i} because its starting year of {row_starting_year} != {starting_year}"
            )
            continue

        # Filter by location
        if row.location != location:
            logger.debug(
                f"Skipping row {i} because its location of {row.location} != {location}"
            )
            continue

        # Parse capacity
        parse_capacity_result = _parse_capacity(row.capacity)
        if parse_capacity_result is None:
            logger.error(f'Row {i}: Failed to parse capacity "{row.capacity}"')
            continue  # Maybe this should raise an exception instead of continuing
        capacity_range_start, capacity_range_end, capacity_per = parse_capacity_result

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
    # fields_reference : list[str] = csvFile[0].strip("\r").split(",")
    # rooms = []
    # building_seed = matching.load_seed()
    # aliases = matching.load_aliases()
    # for data in csv.DictReader(csvFile):
    #     if (len(data) <= 1):
    #         continue
    #     if (data["Location"] != "West Lafayette"):
    #         continue
    #     if (data["Term"][0:4] != str(startingYear)):
    #         continue

    #     building_id     : str = ""
    #     id              : str = data["Room Type ID"]
    #     roomType        : str = data["Room Type"]
    #     term            : str = data["Term"]
    #     category        : str = data["Category"]
    #     amount          : int = int(data["Amount"])
    #     buildings       : list[str] = []
    #     apartment       : bool = True if (data["UR Boiler Apartment"] == "TRUE") else False
    #     totalCapacity   : str = ""
    #     capacity        : str = data["Capacity"]
    #     airConditioning : bool = True if (data["Air Conditioning"] == "True") else False
    #     bath            : bool = True if (data["Bath"] == "True") else False
    #     normal_building : str = matching.normalize(data["Building"])

    #     if normal_building in aliases.keys():
    #         buildings = aliases[normal_building]
    #     else:
    #         buildings = [data["Building"]]
    #     for building in buildings:
    #         for i in building_seed:
    #             if i.name == building:
    #                 building_id = i.id
    #         if building_id == "":
    #             continue
    #         totalCapacity = get_capacity(roomType, capacity)
    #         a = Room(buildingId=building_id, capacity=int(totalCapacity), housingRate=amount)
    #         rooms.append(a)
    # return rooms


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


# TODO test
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


# def get_capacity(roomType: str, capacity: str):
#     if capacity.isdigit():
#         totalCapacity = capacity
#     elif capacity.find("-") > -1:
#         totalCapacity = capacity[capacity.find("-") + 1]
#     elif capacity.find("/Room") > -1:
#         totalCapacity = capacity[0]
#     elif roomType.find("for") > -1:
#         totalCapacity = roomType[roomType.find("for") + 4]
#     else:
#         totalCapacity = capacity[0]
#     return totalCapacity
