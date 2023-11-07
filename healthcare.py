import json

from fastapi import APIRouter

from models import HealthFacility, FacilityUpdate

router = APIRouter()

json_filename = "db/health_facilities.json"

with open(json_filename, "r") as read_file:
    facilities = json.load(read_file)


def get_facility_ids():
    return [facility["facility_id"] for facility in facilities]


@router.get("/")
async def get_health_facilities():
    fac_name_list = []
    for facility in facilities:
        fac_name_list.append(facility['facility_name'])
    return fac_name_list


@router.get("/{facility_id}")
async def get_health_facility_by_id(facility_id: str):
    facility_ids = get_facility_ids()
    if facility_id not in facility_ids:
        return {"message": "The facility you are looking for is not available"}
    for facility in facilities:
        if facility['facility_id'] == facility_id:
            return facility
    return None


@router.post("/{facility_id}")
async def create_health_facility(facility_id: str, add_facility: HealthFacility):
    add_facility.dict()['facility_id'] = facility_id
    facility_ids = get_facility_ids()
    if facility_id in facility_ids:
        return {"message": "The facility with ID: " + facility_id + " is already there"}

    for facility in facilities:
        if add_facility.coordinates.longitude == facility['coordinates'][
            'longitude'] and add_facility.coordinates.latitude == facility['coordinates']['latitude']:
            return {"message": "The facility at that coordinate already exists"}

    add_facility.facility_id = facility_id
    facilities.append(add_facility.dict())
    with open(json_filename, "w") as write_file:
        json.dump(facilities, write_file)

    return {"message": "Facility added successfully"}


@router.put("/{facility_id}")
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


@router.delete('/{facility_id}')
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
