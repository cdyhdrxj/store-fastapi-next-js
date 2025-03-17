from fastapi import APIRouter, HTTPException, Depends, status

from models.item import Item, ItemReadImages, CoverUpdate
from models.cover import Cover
from api.routs.item import update_item
from api.deps import SessionDep
from general.image import ImageFile, image_upload, image_delete
from general.auth import Role
from general.permission_checker import PermissionChecker

router = APIRouter(
    prefix="/items/cover",
    tags=["Товары"],
)

@router.post("/{item_id}", response_model=ItemReadImages)
def create_cover(
    item_id: int,
    file: ImageFile,
    session: SessionDep,
    authorize: bool = Depends(PermissionChecker(roles=[Role.MANAGER, Role.ADMIN]))
):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    if item.cover_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Item already has a cover")

    file_name = image_upload(file)
    if not file_name:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upload image")

    image = Cover(name=file_name)
    db_image = Cover.model_validate(image)
    session.add(db_image)
    session.commit()
    session.refresh(db_image)

    new_item = CoverUpdate(cover_id=db_image.id)
    return update_item(item_id, new_item, session)


@router.delete("/{item_id}")
def delete_cover(
    item_id: int,
    session: SessionDep,
    authorize: bool = Depends(PermissionChecker(roles=[Role.MANAGER, Role.ADMIN]))
):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    cover = session.get(Cover, item.cover_id)
    if not cover:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item's cover not found")

    if not image_delete(cover.name):
        raise HTTPException(status_code=500, detail="Unable to delete item's cover")

    session.delete(cover)
    session.commit()

    return {"ok": True}
