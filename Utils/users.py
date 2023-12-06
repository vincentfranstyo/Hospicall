from fastapi import APIRouter, Depends, HTTPException, status
import json
from Models.user import UserJSON, UserUpdate

from Utils.auth import get_current_user

user = APIRouter(tags=['user'])

json_filename = "Data/users.json"

with open(json_filename, "r") as read_file:
    users = json.load(read_file)


def get_users_id():
    return [user["id"] for user in users]


def not_user(user: UserJSON = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Please do register")


def not_admin(user: UserJSON = Depends(get_current_user)):
    if not user.admin_status:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not have admin privileges")


@user.get("/")
async def get_users():
    users_fullname = []
    for user in users:
        users_fullname.append(user['first_name'] + " " + user['last_name'])
    return users_fullname


@user.get("/{user_id}")
async def get_user_by_id(user_id: str, user: UserJSON = Depends(get_current_user)):
    not_user(user)
    users_id = get_users_id()
    if user_id not in users_id:
        return {"message": "The user you are looking for is nowhere to be found"}
    for user in users:
        if user['id'] == user_id:
            return user
    return None


@user.put("/user")
async def update_health_facility(user_id: str, update_user: UserUpdate, user: UserJSON = Depends(get_current_user)):
    not_admin(user)
    users_id = get_users_id()
    if user_id not in users_id:
        return {"The user you are looking for is not available"}

    for user in users:
        if user['id'] == user_id:
            update_data = {key: value for key, value in update_user.dict().items() if value}
            user.update(update_data)

    with open(json_filename, 'w') as update_file:
        json.dump(users, update_file, indent=4)

    return {"message": "users updated successfully"}


@user.delete('/delete_user')
async def delete_health_facility(user_id: str, user: UserJSON = Depends(get_current_user)):
    not_admin(user)
    global users
    users_id = get_users_id()
    if user_id not in users_id:
        return {"message": "The user you are looking for is not available"}

    user_to_delete = []
    for user in users:
        if user['id'] == user_id:
            user_to_delete.append(user)
    if not user_to_delete:
        return {"message": "The user you are looking for is not available"}

    username = user_to_delete[0]['username']
    users = [user for user in users if user not in user_to_delete]

    with open(json_filename, 'w') as delete_file:
        json.dump(users, delete_file, indent=4)

    return {"Message": "User with " + username + " is deleted successfully"}
