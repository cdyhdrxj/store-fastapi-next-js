from fastapi import APIRouter, Depends, HTTPException, status, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Annotated
from fastapi import Response
from general.auth import Role, create_access_token, delete_cookie, ACCESS_TOKEN_EXPIRE_MINUTES
from general.password import verify_password
from general.user import read_user_by_username
from general.permission_checker import PermissionChecker
from api.deps import SessionDep

router = APIRouter(
    prefix="/login",
    tags=["Аутентификация"],
)

@router.post("/")
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
    response: Response,
):
    user = read_user_by_username(form_data.username, session)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректный логин или пароль",
        )
    access_token = create_access_token(user, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    response.set_cookie(
        key="role",
        value=user.role.value,
        httponly=True,
        secure=True,
        max_age=30 * 60,  # 0.5 часа
        path="/",
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        max_age=30 * 60,  # 0.5 часа
        path="/",
    )
    
    return { "username": user.username }


@router.post("/logout/")
def logout(response: Response):
   delete_cookie(response)
   return {"ok": True}


from models.user import UserRead
from general.auth import get_current_active_user

@router.get("/me/", response_model=UserRead)
def read_users_me(
    current_user: Annotated[UserRead, Depends(get_current_active_user)],
    authorize: bool = Depends(PermissionChecker(roles=[Role.USER, Role.MANAGER, Role.ADMIN]))
):
    return current_user
