from fastapi import APIRouter, HTTPException, Query, Depends, status
from typing import Annotated
from sqlmodel import select

from models.item import Item, ItemCreate, ItemRead, ItemReadImages, ItemUpdate, ItemAdd
from api.deps import SessionDep
from general.auth import Role
from general.permission_checker import PermissionChecker

router = APIRouter(
    prefix="/items",
    tags=["Товары"],
)

@router.post("/", response_model=ItemReadImages)
def create_item(
    item: ItemCreate,
    session: SessionDep,
    authorize: bool = Depends(PermissionChecker(roles=[Role.MANAGER, Role.ADMIN]))
):
    db_item = Item.model_validate(item)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.get("/", response_model=list[ItemRead])
def read_items(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 20,
    search: str = "",
):
    query = select(Item)
    if search:
        query = query.where(Item.name.contains(search) | Item.description.contains(search))
    
    items = session.exec(query.offset(offset).limit(limit)).all()    
    return items


@router.get("/{item_id}", response_model=ItemReadImages)
def read_item(item_id: int, session: SessionDep):
    item_db = session.get(Item, item_id)
    if not item_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")
    return item_db


@router.patch("/{item_id}", response_model=ItemReadImages)
def update_item(
    item_id: int,
    item: ItemUpdate,
    session: SessionDep,
    authorize: bool = Depends(PermissionChecker(roles=[Role.MANAGER, Role.ADMIN]))
):
    item_db = session.get(Item, item_id)
    if not item_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")
    item_data = item.model_dump(exclude_unset=True)
    item_db.sqlmodel_update(item_data)
    session.add(item_db)
    session.commit()
    session.refresh(item_db)
    return item_db


@router.patch("/add/{item_id}", response_model=ItemRead)
def update_quantity(
    item_id: int,
    item: ItemAdd,
    session: SessionDep,
    authorize: bool = Depends(PermissionChecker(roles=[Role.MANAGER, Role.ADMIN]))
):
    item_db = session.get(Item, item_id)
    if not item_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")
    if item.quantity <= 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Нельзя уменьшить количество товара")
    item.quantity += item_db.quantity
    item_data = item.model_dump(exclude_unset=True)
    item_db.sqlmodel_update(item_data)
    session.add(item_db)
    session.commit()
    session.refresh(item_db)
    return item_db


@router.delete("/{item_id}")
def delete_item(
    item_id: int,
    session: SessionDep,
    authorize: bool = Depends(PermissionChecker(roles=[Role.MANAGER, Role.ADMIN]))
):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")
    session.delete(item)
    session.commit()
    return {"ok": True}
