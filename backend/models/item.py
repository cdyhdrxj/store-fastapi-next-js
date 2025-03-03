from sqlmodel import Field, SQLModel, Relationship

from models.brand import Brand, BrandRead
from models.category import Category, CategoryRead


class ItemBase(SQLModel):
    name: str = Field(max_length=50)
    description: str = Field(max_length=200)
    price: int = Field(ge=0, le=10 ** 8)


class Item(ItemBase, table=True):
    id: int | None = Field(None, primary_key=True)
    brand_id: int = Field(foreign_key="brand.id", ondelete="RESTRICT")
    category_id: int = Field(foreign_key="category.id", ondelete="RESTRICT")
    brand: Brand | None = Relationship()
    category: Category | None = Relationship()


class ItemRead(ItemBase):
    id: int
    brand: Brand = None
    category: Category = None


class ItemCreate(ItemBase):
    brand_id: int
    category_id: int


class ItemUpdate(ItemBase):
    name: str | None = Field(None, max_length=50)
    description: str | None = Field(None, max_length=200)
    price: int | None = Field(None, ge=0, le=10 ** 8)
    brand_id: int | None = None
    category_id: int | None = None
