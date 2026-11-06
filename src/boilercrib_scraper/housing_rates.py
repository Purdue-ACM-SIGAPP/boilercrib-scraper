from requests import get
from models import *
import csv
import datetime as dt
import matching

SOURCE = "https://housing.purdue.edu/data/room-rates.csv"

def get_current_academic_year():
    est_zone = dt.timezone(dt.timedelta(hours=-5))
    today = dt.datetime.now(tz=est_zone)
    if (today.month >= 8):
        return today.year
    else:
        return today.year - 1

def get_capacity(roomType : str, capacity : str):
    if capacity.isdigit():
        totalCapacity = capacity
    elif capacity.find("-") > -1:
        totalCapacity = capacity[capacity.find("-") + 1]
    elif capacity.find("/Room") > -1:
        totalCapacity = capacity[0]
    elif roomType.find("for") > -1:
        totalCapacity = roomType[roomType.find("for") + 4]
    else:
        totalCapacity = capacity[0]
    return totalCapacity

def get_housing_rates(startingYear : int = get_current_academic_year()):
    file : list[str] = get(SOURCE).text.split("\n")
    fields_reference : list[str] = file[0].strip("\r").split(",")
    rooms = []
    building_seed = matching.load_seed()
    aliases = matching.load_aliases()
    for data in csv.DictReader(file):
        if (len(data) <= 1):
            continue
        if (data["Location"] != "West Lafayette"):
            continue
        if (data["Term"][0:4] != str(startingYear)):
            continue
        
        building_id     : str = ""
        id              : str = data["Room Type ID"]
        roomType        : str = data["Room Type"]
        term            : str = data["Term"]
        category        : str = data["Category"]
        amount          : int = int(data["Amount"])
        buildings       : list[str] = []
        apartment       : bool = True if (data["UR Boiler Apartment"] == "TRUE") else False
        totalCapacity   : str = ""
        capacity        : str = data["Capacity"]
        airConditioning : bool = True if (data["Air Conditioning"] == "True") else False
        bath            : bool = True if (data["Bath"] == "True") else False
        normal_building : str = matching.normalize(data["Building"])
        
        if normal_building in aliases.keys():
            buildings = aliases[normal_building]
        else:
            buildings = [data["Building"]]
        for building in buildings:
            for i in building_seed:
                if i.name == building:
                    building_id = i.id
            if building_id == "":
                continue
            totalCapacity = get_capacity(roomType, capacity)
            a = Room(buildingId=building_id, capacity=int(totalCapacity), housingRate=amount)
            rooms.append(a)
    return rooms