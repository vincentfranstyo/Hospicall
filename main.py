import json
import math
import sys
from typing import Optional, Any

from fastapi import FastAPI
from pydantic import BaseModel, validator

app = FastAPI()


class Coordinate(BaseModel):
    longitude: float
    latitude: float

    @validator('longitude')
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('longitude must be between -180 and 180')
        return v

    @validator('latitude')
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('latitude must be between -90 and 90')
        return v


class Address(BaseModel):
    street: str
    city: str
    province: str


class HealthFacility(BaseModel):
    facility_id: str = None
    facility_name: str
    facility_type: str
    address: Address
    coordinates: Coordinate
    phone_number: str
    bed_capacity: int
    doctor_count: int


class FacilityUpdate(BaseModel):
    facility_name: Optional[str]
    facility_type: Optional[str]
    address: Optional[Address]
    phone_number: Optional[str]
    bed_capacity: Optional[int]
    doctor_count: Optional[int]


json_filename = "health_facilities.json"

with open(json_filename, "r") as read_file:
    facilities = json.load(read_file)


def distance_by_long_and_lat(coor1: Coordinate, coor2: Coordinate):
    lon1, lat1 = math.radians(coor1.longitude), math.radians(coor1.latitude)
    lon2, lat2 = math.radians(coor2.longitude), math.radians(coor2.latitude)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = 6371 * c  # Radius of the Earth in kilometers
    return round(distance, 2)


def get_facility_ids():
    return [facility["facility_id"] for facility in facilities]


@app.get("/")
async def root():
    return {"This is a one-call-away hospital line"}


@app.get("/health-facilities")
async def get_health_facilities():
    fac_name_list = []
    for facility in facilities:
        fac_name_list.append(facility['facility_name'])
    return fac_name_list


@app.get("/health-facility/{facility_id}")
async def get_health_facility_by_id(facility_id: str):
    facility_ids = get_facility_ids()
    if facility_id not in facility_ids:
        return {"message": "The facility you are looking for is not available"}
    for facility in facilities:
        if facility['facility_id'] == facility_id:
            return facility
    return None


@app.post("/health-facility/{facility_id}")
async def create_health_facility(facility_id: str, add_facility: HealthFacility):
    add_facility.dict()['id'] = facility_id
    facility_ids = get_facility_ids()
    if facility_id in facility_ids:
        return {"message": "The facility with ID: " + facility_id + " is already there"}

    for facility in facilities:
        if add_facility.coordinates.longitude == facility['coordinates']['longitude'] and add_facility.coordinates.latitude == facility['coordinates']['latitude']:
            return {"message": "The facility at that coordinate already exists"}

    add_facility.facility_id = facility_id
    facilities.append(add_facility.dict())
    with open(json_filename, "w") as write_file:
        json.dump(facilities, write_file)

    return {"message": "Facility added successfully"}


@app.put("/health-facility/{facility_id}")
async def update_health_facility(facility_id: str, update_fac: FacilityUpdate):
    facility_ids = get_facility_ids()
    if facility_id not in facility_ids:
        return {"The facility you are looking for is not available"}

    for facility in facilities:
        if facility['facility_id'] == facility_id:
            update_data = {key: value for key, value in update_fac.dict().items() if value}
            facility.update(update_data)

    with open(json_filename, 'w') as update_file:
        json.dump(facilities, update_file)

    return {"message": "Facilities updated successfully"}


@app.delete('/health-facility/{facility_id}')
async def delete_health_facility(facility_id: str):
    global facilities
    facility_ids = get_facility_ids()
    if facility_id not in facility_ids:
        return {"message": "The facility you are looking for is not available"}

    facilities_to_delete = []
    for facility in facilities:
        if facility['facility_id'] == facility_id:
            facilities_to_delete.append(facility)
    if not facilities_to_delete:
        return {"message": "The facility you are looking for is not available"}

    fac_name = facilities_to_delete[0]['facility_name']
    facilities = [facility for facility in facilities if facility not in facilities_to_delete]

    with open(json_filename, 'w') as delete_file:
        json.dump(facilities, delete_file)

    return {"Message": "Healthcare " + fac_name + " deleted successfully"}


@app.get("/call-nearest-health-facility/")
async def call_nearest_health_facility(longitude: float, latitude: float):
    current_coor = Coordinate(longitude=longitude, latitude=latitude)
    curr_dis = sys.maxsize
    closest_facilities = []
    for facility in facilities:
        facility_coor = Coordinate(longitude=facility['coordinates']['longitude'], latitude=facility['coordinates']['latitude'])
        dis = distance_by_long_and_lat(facility_coor, current_coor)
        if dis < curr_dis:
            curr_dis = dis
            closest_facilities = [
                {"Message": "The closest facility is " + facility['facility_name'] + ". The phone number is " + facility['phone_number']}
            ]

        elif dis == curr_dis:
            closest_facilities.append({"Another closest facility is " + facility['facility_name'] + ". The phone number is " + facility['phone_number']})

    return {"Message": "We are making a call and giving a notification to the facilities", "closest_facilities": closest_facilities}
