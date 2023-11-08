from fastapi import APIRouter

from db.supabase_manager import create_supabase_client
from models import HealthFacility, FacilityUpdate

router = APIRouter()
supabase_client = create_supabase_client()


def get_facilities():
    facs = supabase_client.from_("healthcares").select("*").execute()
    return facs


def get_facility_ids():
    facs = get_facilities()
    return [facility["facility_id"] for facility in facs]


def save_to_db(healthcares):
    try:
        facs = supabase_client.from_("healthcares").insert(healthcares).execute()
        return facs
    except Exception as e:
        print("Error inserting")
        return "Error inserting"


facilities = get_facilities()


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
    try:
        add_facility.dict()['facility_id'] = facility_id
        facility_ids = get_facility_ids()
        if facility_id in facility_ids:
            return {"message": "The facility with ID: " + facility_id + " is already there"}

        for facility in facilities:
            if add_facility.coordinates.longitude == facility['coordinates']['longitude'] and add_facility.coordinates.latitude == facility['coordinates']['latitude']:
                return {"message": "The facility at that coordinate already exists"}

        add_facility.facility_id = facility_id
        facilities.append(add_facility.dict())
        facs = save_to_db(facilities)
        return [{"facilities": facs}, {"message": "Facility added successfully"}] if facs else [
            {"message": "failed to add facility"}]
    except Exception as e:
        print("Error", e)
        return [{"message": "Error adding facility"}]


@router.put("/{facility_id}")
async def update_health_facility(facility_id: str, update_fac: FacilityUpdate):
    try:
        facility_ids = get_facility_ids()
        if facility_id not in facility_ids:
            return {"The facility you are looking for is not available"}

        for facility in facilities:
            if facility['facility_id'] == facility_id:
                update_data = {key: value for key, value in update_fac.dict().items() if value}
                facility.update(update_data)

        facs = save_to_db(facilities)
        return [{"facilities": facs}, {"message": "Facility updated successfully"}] if facs else [
            {"message": "failed to update facility"}]
    except Exception as e:
        print("Error: ", e)
        return [{"message": "failed to update facility"}]


@router.delete('/{facility_id}')
async def delete_health_facility(facility_id: str):
    healthcares = get_facilities()
    facility_ids = get_facility_ids()
    if facility_id not in facility_ids:
        return {"message": "The facility you are looking for is not available"}

    facilities_to_delete = []
    for facility in healthcares:
        if facility['facility_id'] == facility_id:
            facilities_to_delete.append(facility)
    if not facilities_to_delete:
        return {"message": "The facility you are looking for is not available"}

    fac_name = facilities_to_delete[0]['facility_name']
    healthcares = [facility for facility in healthcares if facility not in facilities_to_delete]
    try:
        facs = save_to_db(healthcares)
        return [{"facilities": healthcares},
                {"Message": "Healthcare " + fac_name + " deleted successfully"}] if facs else [
            {"message": "Failed to delete " + fac_name}]

    except Exception as e:
        print("Error: ", e)
        return [{"message": "Failed to delete " + fac_name}]
