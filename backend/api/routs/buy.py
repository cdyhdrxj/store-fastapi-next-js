from fastapi import APIRouter, HTTPException, Depends, status

from models.item import Item, ItemRead, ItemAdd
from api.deps import SessionDep
from general.auth import Role
from general.permission_checker import PermissionChecker

router = APIRouter(
    prefix="/buy",
    tags=["Купить"],
)

@router.patch("/{item_id}", response_model=ItemRead)
def buy_item(
    item_id: int,
    item: ItemAdd,
    session: SessionDep,
    authorize: bool = Depends(PermissionChecker(roles=[Role.USER]))
):
    item_db = session.get(Item, item_id)
    if not item_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")
    if item.quantity <= 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Некорректное количество товара")
    item.quantity = item_db.quantity - item.quantity
    if item.quantity < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Недостаточно товара")
    item_data = item.model_dump(exclude_unset=True)
    item_db.sqlmodel_update(item_data)
    session.add(item_db)
    session.commit()
    session.refresh(item_db)
    return item_db
