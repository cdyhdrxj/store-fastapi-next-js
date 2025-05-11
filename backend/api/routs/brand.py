from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import select

from models.brand import Brand, BrandCreate, BrandRead, BrandUpdate
from api.deps import SessionDep
from general.permission_checker import PermissionChecker
from general.auth import Role

router = APIRouter(
    prefix="/brands",
    tags=["Бренды"],
)

@router.post("/", response_model=BrandRead)
def create_brand(
    brand: BrandCreate,
    session: SessionDep,
    authorize: bool = Depends(PermissionChecker(roles=[Role.MANAGER, Role.ADMIN]))
):
    db_brand = Brand.model_validate(brand)
    session.add(db_brand)
    session.commit()
    session.refresh(db_brand)
    return db_brand


@router.get("/", response_model=list[BrandRead])
def read_brands(
    session: SessionDep,
    authorize: bool = Depends(PermissionChecker(roles=[Role.MANAGER, Role.ADMIN]))
):
    brands = session.exec(select(Brand)).all()
    return brands


@router.get("/{brand_id}", response_model=BrandRead)
def read_brand(
    brand_id: int,
    session: SessionDep,
    authorize: bool = Depends(PermissionChecker(roles=[Role.MANAGER, Role.ADMIN]))
):
    brand_db = session.get(Brand, brand_id)
    if not brand_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Бренд не найден")
    return brand_db


@router.patch("/{brand_id}", response_model=BrandRead)
def update_brand(
    brand_id: int,
    brand: BrandUpdate,
    session: SessionDep,
    authorize: bool = Depends(PermissionChecker(roles=[Role.MANAGER, Role.ADMIN]))
):
    brand_db = session.get(Brand, brand_id)
    if not brand_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Бренд не найден")
    brand_data = brand.model_dump(exclude_unset=True)
    brand_db.sqlmodel_update(brand_data)
    session.add(brand_db)
    session.commit()
    session.refresh(brand_db)
    return brand_db


@router.delete("/{brand_id}")
def delete_brand(
    brand_id: int,
    session: SessionDep,
    authorize: bool = Depends(PermissionChecker(roles=[Role.MANAGER, Role.ADMIN]))
):
    brand = session.get(Brand, brand_id)
    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Бренд не найден")
    session.delete(brand)
    session.commit()
    return {"ok": True}
