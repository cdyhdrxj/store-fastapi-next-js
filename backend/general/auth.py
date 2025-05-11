from datetime import datetime, timedelta, timezone
from typing import Annotated
from enum import Enum

import jwt
from fastapi import Depends, HTTPException, status, Cookie, Response
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from pydantic import BaseModel

from models.user import UserRead, Role, UserToken

from general.user import read_user_by_username
from api.deps import SessionDep

SECRET_KEY = "36979beb55696b6bc0ecd085250991c8ea677d9c20f4792f3d30da7f6b84fb71"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class T(str, Enum):
    USERNAME = "sub"
    ROLE = "role"
    TIME_EXPIRE = "exp"

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
    role: Role | None = None

def create_access_token(user: UserToken, expires_delta: timedelta) -> str:
    to_encode = {
        T.USERNAME: user.username,
        T.ROLE: user.role,
        T.TIME_EXPIRE: datetime.now(timezone.utc) + expires_delta
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(
    session: SessionDep,
    response: Response,
    access_token: str = Cookie(...),
) -> UserRead:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Необходимо авторизоваться",
    )
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get(T.USERNAME)
        role = payload.get(T.ROLE)

        if username is None or role is None:
            delete_cookie(response)
            raise credentials_exception
        token_data = TokenData(username=username, role=role)
    except ExpiredSignatureError:
        delete_cookie(response)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Время жизни токена истекло")
    except InvalidTokenError:
        delete_cookie(response)
        raise credentials_exception

    user = read_user_by_username(token_data.username, session)
    if user is None or user.role != token_data.role:
        delete_cookie(response)
        raise credentials_exception
    return user


def get_current_active_user(
    current_user: Annotated[UserRead, Depends(get_current_user)]
) -> UserRead:
    return current_user


def delete_cookie(response: Response):
    response.delete_cookie(
        key="role",
        httponly=True,
        secure=True,
        path="/",
    )

    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,
        path="/",
    )
 