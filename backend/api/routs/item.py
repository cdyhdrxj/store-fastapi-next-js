from typing import Annotated
from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select

from models.item import Item, ItemCreate, ItemRead, ItemReadImages, ItemUpdate
from api.deps import SessionDep

router = APIRouter(
    prefix="/items",
    tags=["item"],
)

@router.post("/", response_model=ItemReadImages)
def create_item(item: ItemCreate, session: SessionDep):
    db_item = Item.model_validate(item)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.get("/", response_model=list[ItemRead])
def read_items(
    session: SessionDep,
    search: str = "",
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 20,
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
        raise HTTPException(status_code=404, detail="Item not found")
    return item_db


@router.patch("/{item_id}", response_model=ItemReadImages)
def update_item(item_id: int, item: ItemUpdate, session: SessionDep):
    item_db = session.get(Item, item_id)
    if not item_db:
        raise HTTPException(status_code=404, detail="Item not found")
    item_data = item.model_dump(exclude_unset=True)
    item_db.sqlmodel_update(item_data)
    session.add(item_db)
    session.commit()
    session.refresh(item_db)
    return item_db


@router.delete("/{item_id}")
def delete_item(item_id: int, session: SessionDep):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    session.delete(item)
    session.commit()
    return {"ok": True}
