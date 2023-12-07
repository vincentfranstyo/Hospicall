from fastapi import APIRouter, Depends, HTTPException, status
import json
from Models.user import UserJSON, UserUpdate, UserIn

from Utils.auth import get_current_user, register
from Utils.read_file import read_user_file
from Utils.write_file import write_user_file

user = APIRouter(tags=['User'])

user_json = "Data/users.json"


users = read_user_file(user_json)


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


@user.post('/add_user')
async def add_user(new_user: UserIn, user: UserJSON = Depends(get_current_user)):
    not_admin(user)
    made_user = await register(new_user)
    return made_user


@user.put("/edit_user")
async def update_user(user_id: str, update_user: UserUpdate, user: UserJSON = Depends(get_current_user)):
    not_admin(user)
    users_id = get_users_id()
    if user_id not in users_id:
        return {"The user you are looking for is not available"}

    for user in users:
        if user['id'] == user_id:
            update_data = {key: value for key, value in update_user.dict().items() if value}
            user.update(update_data)

    write_user_file(user_json, users)

    return {"message": "users updated successfully"}


@user.delete('/delete_user')
async def delete_user(user_id: str, user: UserJSON = Depends(get_current_user)):
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

    write_user_file(user_json, users)

    return {"Message": "User with username " + username + " is deleted successfully"}
