from fastapi import APIRouter, HTTPException, Depends, status

from models.item import Item, ItemReadImages, Image, ImageCreate
from api.deps import SessionDep
from general.image import ImageFile, image_upload, image_delete
from general.auth import Role
from general.permission_checker import PermissionChecker

router = APIRouter(
    prefix="/items/images",
    tags=["Товары"],
)

@router.post("/{item_id}", response_model=ItemReadImages)
def create_image(
    item_id: int,
    file: ImageFile,
    session: SessionDep,
    authorize: bool = Depends(PermissionChecker(roles=[Role.MANAGER, Role.ADMIN]))
):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")

    file_name = image_upload(file)
    if not file_name:
        raise HTTPException(status_code=500, detail="Не удалось загрузить изображение")

    image = ImageCreate(name=file_name, item_id=item_id)
    db_image = Image.model_validate(image)
    session.add(db_image)
    session.commit()
    session.refresh(db_image)

    session.refresh(item)
    return item


@router.delete("/{image_id}")
def delete_image(
    image_id: int,
    session: SessionDep,
    authorize: bool = Depends(PermissionChecker(roles=[Role.MANAGER, Role.ADMIN]))
):
    image = session.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Изображение не найдено")

    if not image_delete(image.name):
        raise HTTPException(status_code=500, detail="Невозможно удалить изображение")

    session.delete(image)
    session.commit()

    return {"ok": True}
