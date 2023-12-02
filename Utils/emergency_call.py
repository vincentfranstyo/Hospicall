from math import cos, asin, sqrt, pi
import sys
import json

from Models.models import Coordinate, CallLog
from fastapi import APIRouter

router = APIRouter()

call_logs_json = 'Data/call_logs.json'
with open(call_logs_json, "r") as read_file:
    call_logs = json.load(read_file)

healthcare_json = "Data/health_facilities.json"
with open(healthcare_json, "r") as read_file:
    facilities = json.load(read_file)


def distance_by_long_and_lat(coor1: Coordinate, coor2: Coordinate):
    r = 6371  # Radius of the earth in km
    p = pi / 180
    lat1 = coor1.latitude
    lat2 = coor2.latitude
    lon1 = coor1.longitude
    lon2 = coor2.longitude

    a = 0.5 - cos((lat2 - lat1) * p) / 2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
    d = 2 * r * asin(sqrt(a))  # Distance in km
    return d


@router.get("/")
async def get_healthcare_number(longitude: float, latitude: float):
    closest_facilities = {}
    current_coor = Coordinate(longitude=longitude, latitude=latitude)
    curr_dis = sys.maxsize

    for facility in facilities:
        facility_coor = Coordinate(longitude=facility['coordinates']['longitude'],
                                   latitude=facility['coordinates']['latitude'])
        dis = distance_by_long_and_lat(facility_coor, current_coor)

        if dis < curr_dis:
            curr_dis = dis
            closest_facilities = {'facility_name': facility['facility_name'], 'phone_number': facility['phone_number']}

    return {"closest_facilities": closest_facilities}


@router.post('/')
async def make_call(longitude: float, latitude: float):
    closest_facilities = await get_healthcare_number(longitude, latitude)
    closest_facility = closest_facilities['closest_facilities']
    callee_number = closest_facility['phone_number']

    if closest_facility:
        add_call = CallLog(callee_number=callee_number)
        call_added = add_call.dict()

        call_logs.append(call_added)

        with open(call_logs_json, "w") as call_file:
            json.dump(call_logs, call_file, indent=4)

    return {"message": f"Your call to {closest_facility['facility_name']} has been made"}
