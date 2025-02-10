from typing import Annotated
from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select

from models.category import Category, CategoryCreate, CategoryUpdate, CategoryPublic
from api.deps import SessionDep

router = APIRouter(
    prefix="/categories",
    tags=["category"],
)

@router.post("/", response_model=CategoryPublic)
def create_category(category: CategoryCreate, session: SessionDep):
    db_category = Category.model_validate(category)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


@router.get("/", response_model=list[CategoryPublic])
def read_categories(session: SessionDep):
    categorys = session.exec(select(Category)).all()
    return categorys


@router.get("/{category_id}", response_model=CategoryPublic)
def read_category(category_id: int, session: SessionDep):
    category_db = session.get(Category, category_id)
    if not category_db :
        raise HTTPException(status_code=404, detail="Category not found")
    return category_db 


@router.patch("/{category_id}", response_model=CategoryPublic)
def update_category(category_id: int, category: CategoryUpdate, session: SessionDep):
    category_db = session.get(Category, category_id)
    if not category_db:
        raise HTTPException(status_code=404, detail="Category not found")
    category_data = category.model_dump(exclude_unset=True)
    category_db.sqlmodel_update(category_data)
    session.add(category_db)
    session.commit()
    session.refresh(category_db)
    return category_db


@router.delete("/{category_id}")
def delete_category(category_id: int, session: SessionDep):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    session.delete(category)
    session.commit()
    return {"ok": True}
