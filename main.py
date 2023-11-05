import json

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()


class Coordinate(BaseModel):
    latitude: float
    longitude: float


class Address(BaseModel):
    street: str
    city: str
    province: str


class HealthFacility(BaseModel):
    facility_name: str
    facility_type: str
    address: Address
    coordinate: Coordinate
    bed_capacity: int
    doctor_count: int


class FacilityUpdate(BaseModel):
    facility_id: Optional[str]
    facility_name: Optional[str]
    facility_type: Optional[str]
    address: Optional[dict]
    bed_capacity: Optional[int]
    doctor_count: Optional[int]


json_filename = "health_facilities.json"

with open(json_filename, "r") as read_file:
    facilities = json.load(read_file)


async def get_facility_ids():
    return [facility["facility_id"] for facility in facilities]


@app.get("/")
async def root():
    return {"This is a one-call-away hospital line"}


@app.get("/health-facilities")
async def get_health_facilities():
    fac_name_list = []
    for facility in facilities:
        fac_name_list.append(facility.name)
    return fac_name_list


@app.get("/health-facility/{facility_id}")
async def get_health_facility_by_id(facility_id: str):
    if facility_id not in get_facility_ids():
        return {"message": "The facility you are looking for is not available"}
    for facility in facilities:
        if facility.facility_id == facility_id:
            return facility
    return None


@app.post("/health-facility/{facility_id}")
async def create_health_facility(facility_id: str, add_facility: HealthFacility):
    add_facility.model_dump()['id'] = facility_id
    facility_ids = get_facility_ids()
    if facility_id in facility_ids:
        return {"message": "The facility with ID: " + facility_id + " is already there"}

    for facility in facilities:
        if add_facility['coordinates'] == facility['coordinates']:
            return {"message": "The facility at that coordinate already exists"}

    facilities.append(add_facility.model_dump())
    with open(json_filename, "w") as write_file:
        json.dump(facilities, write_file)

    return {"message": "Facility added successfully"}


@app.put("/health-facility/{facility_id}")
async def update_health_facility(facility_id: str, update_fac: FacilityUpdate):
    facility_ids = get_facility_ids()
    if facility_id not in facility_ids:
        return {"The facility you are looking for is not available"}

    for facility in facilities:
        if facility['id'] == facility_id:
            update_data = {key: value for key, value in update_fac.items() if value}
            facility.update(update_data)

    with open(json_filename, 'w') as update_file:
        json.dump(facilities, update_file)

    return {"message": "Facilities updated successfully"}


@app.delete('/health-facility/{facility_id}')
async def delete_health_facility(facility_id: str):
    facility_ids = get_facility_ids()
    if facility_id not in facility_ids:
        return {"message": "The facility you are looking for is not available"}

    for facility in facilities:
        if facility['facility_id'] == facility_id:
            del facility

    with open(json_filename, 'w') as delete_file:
        json.dump(facilities, delete_file)


@app.get("/call-nearest-health-facility")
async def call_nearest_health_facility(coordinate: Coordinate):
    return None
