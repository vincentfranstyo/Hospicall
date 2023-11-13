from pydantic import BaseModel


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
