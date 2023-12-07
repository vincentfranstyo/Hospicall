from fastapi import APIRouter, Depends, HTTPException, status
import json
from Models.user import UserJSON

from Models.models import HealthFacility, FacilityUpdate
from Utils.auth import get_current_user
from Utils.users import not_user, not_admin

json_filename = "Data/health_facilities.json"
healthcares = APIRouter(tags=["Healthcares"])

with open(json_filename, "r") as read_file:
    facilities = json.load(read_file)


def get_facility_ids():
    return [facility["facility_id"] for facility in facilities]


@healthcares.get("/")
async def get_health_facilities(user: UserJSON = Depends(get_current_user)):
    not_user(user)
    fac_name_list = []
    for facility in facilities:
        fac_name_list.append(facility['facility_name'])
    return fac_name_list


@healthcares.get("/{facility_id}")
async def get_health_facility_by_id(facility_id: str, user: UserJSON = Depends(get_current_user)):
    not_user(user)
    facility_ids = get_facility_ids()
    if facility_id not in facility_ids:
        return {"message": "The facility you are looking for is not available"}
    for facility in facilities:
        if facility['facility_id'] == facility_id:
            return facility
    return None


@healthcares.post("/new_facilities")
async def create_health_facility(add_facility: HealthFacility, user: UserJSON = Depends(get_current_user)):
    not_admin(user)

    for facility in facilities:
        if add_facility.coordinates.longitude == facility['coordinates']['longitude'] and add_facility.coordinates.latitude == facility['coordinates']['latitude']:
            return {"message": "The facility at that coordinate already exists"}

    facilities.append(add_facility.dict())
    with open(json_filename, "w") as write_file:
        json.dump(facilities, write_file, indent=4)

    return [{"message": "Facility added successfully"},{"facility_made": add_facility}]


@healthcares.put("/update_facility")
async def update_health_facility(facility_id: str, update_fac: FacilityUpdate, user: UserJSON = Depends(get_current_user)):
    not_admin(user)
    facility_ids = get_facility_ids()
    if facility_id not in facility_ids:
        return {"The facility you are looking for is not available"}

    for facility in facilities:
        if facility['facility_id'] == facility_id:
            update_data = {key: value for key, value in update_fac.dict().items() if value}
            facility.update(update_data)

    with open(json_filename, 'w') as update_file:
        json.dump(facilities, update_file, indent=4)

    return {"message": "Facilities updated successfully"}


@healthcares.delete('/delete_facility')
async def delete_health_facility(facility_id: str, user: UserJSON = Depends(get_current_user)):
    not_admin(user)
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
        json.dump(facilities, delete_file, indent=4)

    return {"Message": "Healthcare " + fac_name + " deleted successfully"}
