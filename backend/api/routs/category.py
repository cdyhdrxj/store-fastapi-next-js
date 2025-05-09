from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import select

from models.category import Category, CategoryCreate, CategoryRead, CategoryUpdate
from api.deps import SessionDep
from general.auth import Role
from general.permission_checker import PermissionChecker

router = APIRouter(
    prefix="/categories",
    tags=["Категории"],
)

@router.post("/", response_model=CategoryRead)
def create_category(
    category: CategoryCreate,
    session: SessionDep,
    # authorize: bool = Depends(PermissionChecker(roles=[Role.MANAGER, Role.ADMIN]))
):
    db_category = Category.model_validate(category)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


@router.get("/", response_model=list[CategoryRead])
def read_categories(session: SessionDep):
    categorys = session.exec(select(Category)).all()
    return categorys


@router.get("/{category_id}", response_model=CategoryRead)
def read_category(category_id: int, session: SessionDep):
    category_db = session.get(Category, category_id)
    if not category_db :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена")
    return category_db 


@router.patch("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int,
    category: CategoryUpdate,
    session: SessionDep,
    # authorize: bool = Depends(PermissionChecker(roles=[Role.MANAGER, Role.ADMIN]))
):
    category_db = session.get(Category, category_id)
    if not category_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена")
    category_data = category.model_dump(exclude_unset=True)
    category_db.sqlmodel_update(category_data)
    session.add(category_db)
    session.commit()
    session.refresh(category_db)
    return category_db


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    session: SessionDep,
    # authorize: bool = Depends(PermissionChecker(roles=[Role.MANAGER, Role.ADMIN]))
):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена")
    session.delete(category)
    session.commit()
    return {"ok": True}
