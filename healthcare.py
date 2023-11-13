from fastapi import APIRouter

from db.supabase_manager import create_supabase_client
from models import HealthFacility, FacilityUpdate

supabase_client = create_supabase_client()


def get_facilities():
    try:
        response = supabase_client.table("healthcares").select("*").execute()
        facs = response.data
        return facs
    except Exception as e:
        print(f"Error retrieving facilities: {str(e)}")
        return {"message": "no data retrieved"}


def get_facility_ids():
    facs = get_facilities()
    facs_ids = [int(facility.get('id')) for facility in facs]
    facs_ids.sort()
    return [str(ids) for ids in facs_ids]


router = APIRouter()
facilities = get_facilities()


@router.get("/")
async def get_health_facilities():
    return get_facilities()


@router.get("/{facility_id}")
async def get_health_facility_by_id(facility_id: str):
    facs = supabase_client.table('healthcares').select("*").eq("id", facility_id).execute()
    return facs.data


@router.post("/{facility_id}")
async def create_health_facility(facility_id: str, add_facility: HealthFacility):
    facility_ids = get_facility_ids()
    if facility_id in facility_ids:
        return {"message": "The facility with ID: " + facility_id + " is already there"}

    fac_added = add_facility.dict()
    try:
        facs = supabase_client.table('healthcares').insert(fac_added).execute()
        return [{"facilities": facs}, {"message": "Facility added successfully"}] if facs else [{"message": "failed to add facility"}]

    except Exception as e:
        print("Error", str(e))
        return [{"message": str(e)}]


@router.put("/{facility_id}")
async def update_health_facility(facility_id: str, update_fac: FacilityUpdate):
    facility_ids = get_facility_ids()
    if facility_id not in facility_ids:
        return {"The facility you are looking for is not available"}

    try:
        old_data = supabase_client.table("healthcares").select("*").eq("id", facility_id).execute()

        if old_data:
            new_data = old_data.data[0]
            updated_data = {key: value for key, value in update_fac.dict().items() if value}

            for key, value in updated_data.items():
                new_data[key] = value

            fac = supabase_client.table("healthcares").update([new_data]).eq("id", facility_id).execute()

            if fac:
                return [{"call updated": fac.data[0]}, {"message": "Call log updated successfully"}]
            else:
                return [{"message": "Facility update failed"}]
        else:
            return [{"message": "The facility you are referring to is not available"}]

    except Exception as e:
        print("Exception", e)
        return [{"Exception": str(e)}]


@router.delete('/{facility_id}')
async def delete_health_facility(facility_id: str):
    fac_ids = get_facility_ids()
    if facility_id not in fac_ids:
        return {"message": "The facility you are looking for is not available"}
    try:
        fac = supabase_client.table("healthcares").delete().eq("id", facility_id).execute()

        return [{"message": "Facility with ID " + facility_id + " deleted successfully"}] if fac else [
            {"message": "Facility delete failed"}]

    except Exception as e:
        print("Exception", e)
        return {"message": str(e)}
