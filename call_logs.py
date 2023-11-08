import json

from fastapi import APIRouter

from db.supabase_manager import create_supabase_client
from models import CallLog, UpdateCall

supabase_client = create_supabase_client()


def get_call_ids():
    calls = get_calls()
    call_ids = [int(call.get('id')) for call in calls]
    call_ids.sort()  # Sort the list in ascending order
    return call_ids


def get_calls():
    try:
        response = supabase_client.table("call_logs").select("*").execute()
        calls = response.data
        return calls
    except Exception as e:
        print(f"Error retrieving calls: {str(e)}")
        return {"message": "no data retrieved"}


def write_to_db(calls):
    json_call = json.dumps(calls)
    supabase_client.table("call_logs").insert(json_call).execute()
    return json_call


# TODO: ini IDnya masi belum auto increment, cuman 1 kali doang. Nextnya ngga increment
router = APIRouter()
call_logs = get_calls()


@router.get('/test')
async def test():
    return get_calls()


@router.get('/')
async def get_call_logs():
    return get_calls()


@router.get('/{call_id}')
async def get_call_log_by_id(call_id: str):
    call = supabase_client.table('call_logs').select("*").eq("id", call_id).execute()
    return call.data


@router.post('/')
async def create_call_log():
    try:
        call_ids = get_call_ids()
        call_id = str(call_ids[-1] + 1)

        add_call = CallLog(id=call_id)
        call_added = add_call.dict()

        call = supabase_client.table("call_logs").insert(call_added).execute()

        if call:
            return [{"call_made": call_added}, {"message": "The call log was added successfully"}]
        else:
            print("Call log addition failed. Retrying with a new ID.")
    except Exception as e:
        print("Error:", e)
        return [{"message": "Call log addition failed"}]


@router.put('/{call_id}')
async def update_call_log(call_id: str, update_call: UpdateCall):
    call_ids = [str(call_id) for call_id in get_call_ids()]
    if call_id not in call_ids:
        return {"message": "The call you are referring to is not available"}

    # TODO: Fix this shit
    try:
        old_data = supabase_client.table("call_logs").select("*").eq("id", call_id).execute()

        updated_data = old_data.data
        if update_call.call_date:
            updated_data['call_date'] = update_call.call_date
        if update_call.call_status:
            updated_data['call_status'] = update_call.call_status

        call = supabase_client.table("call_logs").update(updated_data).eq("id", call_id).execute()

        if call:
            return [{"call updated": call}, {"message": "Call log updated successfully"}]
        else:
            return [{"message": "Call log update failed"}]

    except Exception as e:
        print("Exception", e)
        return [{"call update failed"}]


@router.delete('/{call_id}')
async def delete_call_log(call_id: str):
    try:
        call_ids = [str(call_id) for call_id in get_call_ids()]
        if call_id not in call_ids:
            return {"message": "The call log you are looking for is not available"}

        call = supabase_client.table("call_logs").delete().eq("id", call_id).execute()

        return [{"message": "Call log with ID " + call_id + " deleted successfully"}] if call else [{"message": "Call log delete failed"}]

    except Exception as e:
        print("Exception", e)
        return [{"call delete failed"}]
