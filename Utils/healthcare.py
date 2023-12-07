from fastapi import APIRouter, Depends, HTTPException, status
import json
from Models.user import UserJSON

from Models.models import HealthFacility, FacilityUpdate
from Utils.auth import get_current_user
from Utils.users import not_user, not_admin
from Utils.read_file import read_hf_file
from Utils.write_file import write_hf_file

hf_json = "Data/health_facilities.json"
healthcares = APIRouter(tags=["Healthcares"])

facilities = read_hf_file(hf_json)


def get_facility_ids():
    facilities = read_hf_file(hf_json)
    return [facility["facility_id"] for facility in facilities]


@healthcares.get("/facilities_name")
async def get_health_facilities(user: UserJSON = Depends(get_current_user)):
    not_user(user)
    facilities = read_hf_file(hf_json)
    fac_name_list = []
    for facility in facilities:
        fac_name_list.append(facility['facility_name'])
    return fac_name_list


@healthcares.get("/all_facilities")
async def get_health_facilities(user: UserJSON = Depends(get_current_user)):
    not_user(user)
    facilities = read_hf_file(hf_json)
    return facilities


@healthcares.get("/{facility_id}")
async def get_health_facility_by_id(facility_id: str, user: UserJSON = Depends(get_current_user)):
    not_user(user)
    facilities = read_hf_file(hf_json)
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

    facilities = read_hf_file(hf_json)
    for facility in facilities:
        if add_facility.coordinates.longitude == facility['coordinates']['longitude'] and add_facility.coordinates.latitude == facility['coordinates']['latitude']:
            return {"message": "The facility at that coordinate already exists"}

    facilities.append(add_facility.dict())
    write_hf_file(hf_json, facilities)

    return [{"message": "Facility added successfully"},{"facility_made": add_facility}]


@healthcares.put("/update_facility")
async def update_health_facility(facility_id: str, update_fac: FacilityUpdate, user: UserJSON = Depends(get_current_user)):
    not_admin(user)

    facilities = read_hf_file(hf_json)
    facility_ids = get_facility_ids()
    if facility_id not in facility_ids:
        return {"The facility you are looking for is not available"}

    updated_facility = {}
    for facility in facilities:
        if facility['facility_id'] == facility_id:
            update_data = {key: value for key, value in update_fac.dict().items() if value is not None and value != "string"}
            facility.update(update_data)
            updated_facility = facility

    write_hf_file(hf_json, facilities)

    return [{"message": "Facilities updated successfully"}, {"updated_facility": updated_facility}]


@healthcares.delete('/delete_facility')
async def delete_health_facility(facility_id: str, user: UserJSON = Depends(get_current_user)):
    not_admin(user)

    facilities = read_hf_file(hf_json)
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

    write_hf_file(hf_json, facilities)

    return {"Message": "Healthcare " + fac_name + " deleted successfully"}
