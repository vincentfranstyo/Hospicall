from fastapi import APIRouter, Depends, HTTPException, status

import json

from Models.models import CallLog, UpdateCall
from Models.user import UserJSON
from Utils.auth import get_current_user
from Utils.users import not_user, not_admin

call_logs_json = 'Data/call_logs.json'
calls = APIRouter(tags=["Calls"])

with open(call_logs_json, "r") as read_file:
    call_logs = json.load(read_file)


def get_call_ids():
    return [call['call_id'] for call in call_logs]


@calls.get('/')
async def get_call_logs(user: UserJSON = Depends(get_current_user)):
    not_user(user)
    calls = []
    for call in call_logs:
        calls.append(call)

    return calls


@calls.get('/{call_id}')
async def get_call_log_by_id(call_id: str, user: UserJSON = Depends(get_current_user)):
    not_user(user)
    for call in call_logs:
        if call['call_id'] == call_id:
            return call


@calls.post('/new_log')
async def create_call_log(user: UserJSON = Depends(get_current_user)):
    not_user(user)
    add_call = CallLog()
    call_added = add_call.dict()

    call_logs.append(call_added)

    with open(call_logs_json, "w") as call_file:
        json.dump(call_logs, call_file, indent=4)

    return [{"call_made": call_added}, {"message": "The call logs added successfully"}]


@calls.put("/update_log")
async def update_call_log(call_id: str, update_call: UpdateCall, user: UserJSON = Depends(get_current_user)):
    not_admin(user)
    call_ids = get_call_ids()
    if call_id not in call_ids:
        return {"message": "The call you are referring to is not available"}

    for i, call in enumerate(call_logs):
        if call['call_id'] == call_id:
            update_data = {key: value for key, value in update_call.dict().items() if value}
            call.update(update_data)
            call_logs[i] = call

    with open(call_logs_json, "w") as call_log_file:
        json.dump(call_logs, call_log_file, indent=4)

    return {"message": "Call log updated successfully"}


@calls.delete('/delete_log')
async def delete_call_log(call_id: str, user: UserJSON = Depends(get_current_user)):
    not_admin(user)
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
        json.dump(call_logs, call_file, indent=4)

    return {"Message": "Call log deleted successfully"}
