from requests import get
from models import *
import csv



file : list[str] = get("https://housing.purdue.edu/data/room-rates.csv").text.split("\n")


fields_reference : list[str] = file[0].strip("\r").split(",")

for data in csv.DictReader(file):
    if (len(data) <= 1):
        continue
    if (data["Location"] != "West Lafayette"):
        continue
    if (data["Term"] != "2026-27"):
        continue
    
    # print(data)

    id              : str = data["Room Type ID"]
    roomType        : str = data["Room Type"]
    term            : str = data["Term"]
    category        : str = data["Category"]
    amount          : int = int(data["Amount"])
    building        : str = data["Building"]
    apartment       : bool = True if (data["UR Boiler Apartment"] == "TRUE") else False
    totalCapacity   : int = 1
    capacity        : str = data["Capacity"]
    airConditioning : bool = True if (data["Air Conditioning"] == "True") else False
    bath            : bool = True if (data["Bath"] == "True") else False
    
    if category == "Studio Apt":
        totalCapacity = int(capacity[0])
    elif category.find("Apt") != -1:
        totalCapacity = int(category[0]) * int(capacity[0])
    else:
        if capacity.isdigit():
            totalCapacity = int(capacity)
        elif capacity.find("-") == -1:
            if capacity.find("/Room") != -1:
                totalCapacity = int(capacity[0])
            else:
                if roomType.find("for") == -1:
                    totalCapacity = int(capacity[0])
                else:
                    totalCapacity = int(roomType[roomType.find("for") + 4])
        else:
            #Dealing with ranges
            pass
    # Do stuff here
    a = Room(buildingId=id, capacity=totalCapacity, housingRate=amount)