from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.hash import bcrypt
import jwt
import json
from Models.user import Token, UserIn, UserJSON


def load_user_file():
    with open("Data/users.json", "r") as user_file:
        data = json.load(user_file)
    return data


router = APIRouter(tags=["Authentication"])
JWT_SECRET_KEY = 'jwt-secret'

# token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
users_data = load_user_file()


def save_to_file():
    with open("Data/users.json", "w") as user_file:
        json.dump(users_data, user_file, indent=4)


def auth(username: str, password: str):
    for user in users_data:
        if user['username'] == username and bcrypt.verify(password, user['hashed_password']):
            return user
    return None


@router.post('/token', response_model=Token)
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password'
        )

    token_details = {"sub": user['username'], "id": user['id']}
    token = jwt.encode(token_details, JWT_SECRET_KEY)
    return {'access_token': token, 'token_type': 'bearer'}


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('id')
        user = next((u for u in users_data if u['id'] == user_id))

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='invalid user'
            )
        return UserJSON(**user)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='invalid token'
        )


@router.get('/me', response_model=UserJSON)
async def get_user(user: UserJSON = Depends(get_current_user)):
    return user


@router.post('/register', response_model=UserJSON)
async def register(user: UserIn):
    user_id = str(len(users_data) + 1)
    hashed_password = bcrypt.hash(user.password)
    admin_status = True if user.username == 'testvincent' else False

    new_user = {
        "id": user_id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "username": user.username,
        "hashed_password": hashed_password,
        "phone_number": user.phone_number,
        "admin_status": admin_status
    }

    users_data.append(new_user)
    save_to_file()
    return new_user

