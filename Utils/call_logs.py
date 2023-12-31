from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

import json

from Models.models import CallLog, UpdateCall
from Models.user import UserJSON
from Utils.auth import get_current_user
from Utils.users import not_user, not_admin
from Utils.read_file import read_call_file
from Utils.write_file import write_call_file

call_logs_json = 'Data/call_logs.json'
calls = APIRouter(tags=["Calls"])

call_logs = read_call_file(call_logs_json)


def get_call_ids():
    call_logs = read_call_file(call_logs_json)
    return [call['call_id'] for call in call_logs]


@calls.get('/')
async def get_call_logs(user: UserJSON = Depends(get_current_user)):
    not_user(user)
    call_logs = read_call_file(call_logs_json)
    calls = []
    for call in call_logs:
        calls.append(call)

    return calls


@calls.get('/{call_id}')
async def get_call_log_by_id(call_id: str, user: UserJSON = Depends(get_current_user)):
    not_user(user)
    call_logs = read_call_file(call_logs_json)
    for call in call_logs:
        if call['call_id'] == call_id:
            return call


@calls.post('/new_log')
async def create_call_log(callee_number: Optional[str] = None, caller_number: Optional[str] = None, user: UserJSON = Depends(get_current_user)):
    not_user(user)
    call_logs = read_call_file(call_logs_json)
    if callee_number and caller_number:
        add_call = CallLog(callee_number=callee_number, caller_number=caller_number)
    else:
        add_call = CallLog()

    call_added = add_call.dict()

    call_logs.append(call_added)

    write_call_file(call_logs_json, call_logs)

    return [{"call_made": call_added}, {"message": "The call logs added successfully"}]


@calls.put("/update_log")
async def update_call_log(call_id: str, update_call: UpdateCall, user: UserJSON = Depends(get_current_user)):
    not_admin(user)
    call_logs = read_call_file(call_logs_json)
    call_ids = get_call_ids()
    if call_id not in call_ids:
        return {"message": "The call you are referring to is not available"}

    updated_call = {}

    for i, call in enumerate(call_logs):
        if call['call_id'] == call_id:
            # Update only the fields that are present in the request
            update_data = {key: value for key, value in update_call.dict().items() if value is not None and value != "string"}

            for key, value in call.items():
                if key not in update_data:
                    update_data[key] = value

            call.update(update_data)
            call_logs[i] = call
            updated_call = call

    write_call_file(call_logs_json, call_logs)

    return [{"message": "Call log updated successfully"}, {"updated_data": updated_call}]


@calls.delete('/delete_log')
async def delete_call_log(call_id: str, user: UserJSON = Depends(get_current_user)):
    not_admin(user)
    call_logs = read_call_file(call_logs_json)
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

    write_call_file(call_logs_json, call_logs)

    return {"Message": "Call log deleted successfully"}
