from fastapi import APIRouter, HTTPException
from sqlmodel import select

from models.brand import Brand, BrandCreate, BrandRead, BrandUpdate
from api.deps import SessionDep

router = APIRouter(
    prefix="/brands",
    tags=["brand"],
)

@router.post("/", response_model=BrandRead)
def create_brand(brand: BrandCreate, session: SessionDep):
    db_brand = Brand.model_validate(brand)
    session.add(db_brand)
    session.commit()
    session.refresh(db_brand)
    print(db_brand)
    return db_brand


@router.get("/", response_model=list[BrandRead])
def read_brands(session: SessionDep):
    brands = session.exec(select(Brand)).all()
    return brands


@router.get("/{brand_id}", response_model=BrandRead)
def read_brand(brand_id: int, session: SessionDep):
    brand_db = session.get(Brand, brand_id)
    if not brand_db:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand_db


@router.patch("/{brand_id}", response_model=BrandRead)
def update_brand(brand_id: int, brand: BrandUpdate, session: SessionDep):
    brand_db = session.get(Brand, brand_id)
    if not brand_db:
        raise HTTPException(status_code=404, detail="Brand not found")
    brand_data = brand.model_dump(exclude_unset=True)
    brand_db.sqlmodel_update(brand_data)
    session.add(brand_db)
    session.commit()
    session.refresh(brand_db)
    return brand_db


@router.delete("/{brand_id}")
def delete_brand(brand_id: int, session: SessionDep):
    brand = session.get(Brand, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    session.delete(brand)
    session.commit()
    return {"ok": True}
