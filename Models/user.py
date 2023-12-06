from pydantic import BaseModel
from typing import Optional


# for registration
class UserIn(BaseModel):
    first_name: str
    last_name: str
    email: str
    username: str
    password: str
    phone_number: str


# token response
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# to be written in json file
class UserJSON(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    username: str
    hashed_password: str
    phone_number: str
    admin_status: bool


class UserUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    username: Optional[str]
    phone_number: Optional[str]
