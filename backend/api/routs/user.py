from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import select

from models.user import User, UserCreate, UserRead, UserUpdate
from api.deps import SessionDep
from general.password import get_password_hash
from general.auth import Role
from general.permission_checker import PermissionChecker

router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)

@router.post("/", response_model=UserRead)
def create_user(
    user: UserCreate,
    session: SessionDep,
    authorize: bool = Depends(PermissionChecker(roles=[Role.ADMIN]))
):
    db_user = User.model_validate(user)
    db_user.password_hash = get_password_hash(user.password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.get("/", response_model=list[UserRead])
def read_users(
    session: SessionDep,
    authorize: bool = Depends(PermissionChecker(roles=[Role.ADMIN]))
):
    users = session.exec(select(User)).all()
    return users


@router.get("/{user_id}", response_model=UserRead)
def read_user(
    user_id: int,
    session: SessionDep,
    authorize: bool = Depends(PermissionChecker(roles=[Role.ADMIN]))
):
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    return user_db


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    user: UserUpdate,
    session: SessionDep,
    authorize: bool = Depends(PermissionChecker(roles=[Role.ADMIN]))
):
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    user_data = user.model_dump(exclude_unset=True)
    user_db.sqlmodel_update(user_data)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    session: SessionDep,
    authorize: bool = Depends(PermissionChecker(roles=[Role.ADMIN]))
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    session.delete(user)
    session.commit()
    return {"ok": True}
