import randomtimestamp
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime
import json

call_logs_json = 'Data/call_logs.json'


def get_call_ids():
    with open(call_logs_json, "r") as call_file:
        call_in_logs = json.load(call_file)
    return [call['call_id'] for call in call_in_logs]


# TODO: ini IDnya masi belum auto increment, cuman 1 kali doang. Nextnya ngga increment
class CallLog(BaseModel):
    call_id: str = str(int(get_call_ids()[-1]) + 1)
    call_date: str = datetime.now().strftime("%Y-%m-%d")
    call_time: str = datetime.now().strftime("%H:%M:%S")
    callee_number: str = "+6287890765"
    call_duration: str = randomtimestamp.randomtimestamp().strftime("%H:%M:%S")
    call_status: str = "completed"


class UpdateCall(BaseModel):
    call_date: Optional[str]
    call_time: Optional[str]
    callee_number: Optional[str]
    call_duration: Optional[str]
    call_status: Optional[str]


router = APIRouter()

with open(call_logs_json, "r") as read_file:
    call_logs = json.load(read_file)


@router.get('/')
async def get_call_logs():
    calls = []
    for call in call_logs:
        calls.append(call)

    return calls


@router.get('/{call_id}')
async def get_call_log_by_id(call_id: str):
    for call in call_logs:
        if call['call_id'] == call_id:
            return call


@router.post('/')
async def create_call_log():
    add_call = CallLog()
    call_added = add_call.dict()

    call_logs.append(call_added)

    with open(call_logs_json, "w") as call_file:
        json.dump(call_logs, call_file)

    return [{"call_made": call_added}, {"message": "The call logs added successfully"}]


@router.put("/{call_id}")
async def update_call_log(call_id: str, update_call: UpdateCall):
    call_ids = get_call_ids()
    if call_id not in call_ids:
        return {"message": "The call you are referring to is not available"}

    for i, call in enumerate(call_logs):
        if call['call_id'] == call_id:
            update_data = {key: value for key, value in update_call.dict().items() if value}
            call.update(update_data)
            call_logs[i] = call

    with open(call_logs_json, "w") as call_log_file:
        json.dump(call_logs, call_log_file)

    return {"message": "Call log updated successfully"}


@router.delete('/{call_id}')
async def delete_call_log(call_id: str):
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

    with open(call_logs_json, 'w') as call_file:
        json.dump(call_logs, call_file)

    return {"Message": "Call log deleted successfully"}
