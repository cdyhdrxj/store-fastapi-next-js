from fastapi import APIRouter, HTTPException, Depends, status

from models.item import Item, ItemRead, ItemAdd
from models.user import UserRead
from api.deps import SessionDep
from general.auth import Role, get_current_active_user
from general.permission_checker import PermissionChecker

from api.deps import manager

router = APIRouter(
    prefix="/buy",
    tags=["Купить"],
)


@router.patch("/{item_id}", response_model=ItemRead)
async def buy_item(
    item_id: int,
    item: ItemAdd,
    session: SessionDep,
    current_user: UserRead = Depends(get_current_active_user),
    authorize: bool = Depends(PermissionChecker(roles=[Role.USER]))
):
    item_db = session.get(Item, item_id)
    if not item_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")

    quantity = item.quantity
    if quantity <= 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Некорректное количество товара")
    item.quantity = item_db.quantity - quantity
    if item.quantity < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Недостаточно товара")
    item_data = item.model_dump(exclude_unset=True)
    item_db.sqlmodel_update(item_data)
    session.add(item_db)
    session.commit()
    session.refresh(item_db)

    # Отправляем уведомление всем менеджерам
    await manager.notify_managers_about_buying(
        current_user.username,
        item_db.name,
        quantity,
    )

    return item_db
