import requests

"""
operations:
getCurrentUser
payload={"operationName":"getCurrentUser",
    "query":"query getCurrentUser {\n  currentUser {\n    commonName\n    firstName\n    lastName\n    email\n    favorites {\n      dateAdded\n      favoriteId\n      item {\n        id\n        itemId\n        name\n        isNutritionReady\n        isDiscontinued\n        appearances {\n          date\n          locationName\n          mealName\n          stationName\n          __typename\n        }\n        components {\n          itemId\n          name\n          __typename\n        }\n        traits {\n          name\n          svgIcon\n          svgIconWithoutBackground\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}",
    "variables":{}
    }

getStartLocations
payload={"operationName":"getStartLocations", 
    "query":"query getStartLocations {\n  diningCourtCategories {\n    name\n    diningCourts {\n      id\n      category\n      name\n      formalName\n      lineLength\n      logoUrl\n      upcomingMeals {\n        id\n        name\n        type\n        startTime\n        endTime\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}",
    "variables":{}
    }

getLocationMenu
"""
payload={"operationName":"getLocationMenu",
    "query": "query getLocationMenu($name: String!, $date: Date!) {\n  diningCourtByName(name: $name) {\n    address {\n      city\n      state\n      street\n      zip\n      __typename\n    }\n    formalName\n    id\n    bannerUrl\n    logoUrl\n    name\n    latitude\n    longitude\n    googlePlaceId\n    normalHours {\n      id\n      name\n      effectiveDate\n      days {\n        dayOfWeek\n        meals {\n          endTime\n          name\n          startTime\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    dailyMenu(date: $date) {\n      notes\n      meals {\n        endTime\n        startTime\n        notes\n        name\n        status\n        stations {\n          iconUrl\n          id\n          name\n          notes\n          items {\n            specialName\n            itemMenuId\n            hasComponents\n            item {\n              isFlaggedForCurrentUser\n              isHiddenForCurrentUser\n              isNutritionReady\n              itemId\n              name\n              traits {\n                name\n                svgIcon\n                svgIconWithoutBackground\n                __typename\n              }\n              components {\n                name\n                isFlaggedForCurrentUser\n                isHiddenForCurrentUser\n                isNutritionReady\n                itemId\n                traits {\n                  name\n                  svgIcon\n                  svgIconWithoutBackground\n                  __typename\n                }\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}",
    "variables":{"name": "Earhart", "date": "2012-03-01"}}

a = requests.post("https://api.hfs.purdue.edu/menus/v3/GraphQL", json=payload)

print(a.json())