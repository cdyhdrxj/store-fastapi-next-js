from fastapi import APIRouter, Depends, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Annotated

from general.auth import Role, Token, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from general.user import verify_password, read_user_by_username
from general.permission_checker import PermissionChecker
from api.deps import SessionDep

router = APIRouter(
    prefix="/login",
    tags=["Аутентификация"],
)

@router.post("/", response_model=Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep
) -> Token:
    user = read_user_by_username(form_data.username, session)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(user, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    
    return Token(access_token=access_token, token_type="bearer")

from models.user import UserRead
from general.auth import get_current_active_user

@router.get("/me/", response_model=UserRead)
def read_users_me(
    current_user: Annotated[UserRead, Depends(get_current_active_user)],
    authorize: bool = Depends(PermissionChecker(roles=[Role.USER, Role.MANAGER, Role.ADMIN]))
):
    return current_user