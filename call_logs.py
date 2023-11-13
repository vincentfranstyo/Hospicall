import json

from fastapi import APIRouter

from models import CallLog, UpdateCall
from db.supabase import create_supabase_client

supabase_client = create_supabase_client()


def get_call_ids():
    calls = get_calls()
    return [call['call_id'] for call in calls]


def get_calls():
    calls = supabase_client.from_("Call Logs").select("*").execute()
    return calls


def write_to_db():
    call = supabase_client.from_("Call Logs").insert(call_logs).execute()
    return call

# call_logs_json = 'db/call_logs.json'
#
#
# def get_call_ids():
#     with open(call_logs_json, "r") as call_file:
#         call_in_logs = json.load(call_file)
#     return [call['call_id'] for call in call_in_logs]


# TODO: ini IDnya masi belum auto increment, cuman 1 kali doang. Nextnya ngga increment
router = APIRouter()
call_logs = get_calls()


@router.get('/')
async def get_call_logs():
    calls = get_calls()
    return calls


@router.get('/{call_id}')
async def get_call_log_by_id(call_id: str):
    for call in call_logs:
        if call['call_id'] == call_id:
            return call


@router.post('/')
async def create_call_log():
    try:
        add_call = CallLog()
        call_added = add_call.dict()

        call_logs.append(call_added)

        call = supabase_client.from_("Call Logs").insert(call_logs).execute()
        return [{"call_made": call_added}, {"message": "The call logs added successfully"}] if call else [{"message": "Call Logs addition failed"}]

    except Exception as e:
        print("Error: ", e)
        return [{"message": "Call Logs addition failed"}]


@router.put("/{call_id}")
async def update_call_log(call_id: str, update_call: UpdateCall):
    try:
        call_ids = get_call_ids()
        if call_id not in call_ids:
            return {"message": "The call you are referring to is not available"}

        for i, call in enumerate(call_logs):
            if call['call_id'] == call_id:
                update_data = {key: value for key, value in update_call.dict().items() if value}
                call.update(update_data)
                call_logs[i] = call

        call = write_to_db()

        return [{"call updated": call}, {"message": "Call log updated successfully"}] if call else [{"message": "Call log updated failed"}]

    except Exception as e:
        print("Exception", e)
        return [{"call updated"}]


@router.delete('/{call_id}')
async def delete_call_log(call_id: str):
    try:
        global call_logs
        call_ids = get_call_ids()
        if call_id not in call_ids:
            return {"message": "The call log you are looking for is not available"}

        call_to_delete = []
        for call in call_logs:
            if call['call_id'] == call_id:
                call_to_delete.append(call)

        if not call_to_delete:
            return {"message": "The call log you are looking for is not available"}

        call_logs = [call for call in call_logs if call not in call_to_delete]

        call = write_to_db()

        return [{"call ": call}, {"message": "Call log deleted successfully"}] if call else [
            {"message": "Call log delete failed"}]

    except Exception as e:
        print("Exception", e)
        return [{"call delete failed"}]


