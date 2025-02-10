from sqlmodel import Field, SQLModel

class ItemBase(SQLModel):
    name: str = Field(index=True, max_length=50)
    description: str = Field(index=True, max_length=200)
    price: int = Field(sa_column_kwargs={'nullable': False, 'check_constraints': ['price >= 0', 'price <= 100000000']})


class Item(ItemBase, table=True):
    id: int = Field(default=None, primary_key=True)
    brand_id: int = Field(default=None, foreign_key="brand.id")
    category_id: int = Field(default=None, foreign_key="category.id")


class ItemPublic(ItemBase):
    id: int
    brand_id: int
    category_id: int


class ItemView(ItemBase):
    id: int
    brand: str
    category: str


class ItemCreate(ItemBase):
    brand_id: int
    category_id: int


class ItemUpdate(ItemBase):
    name: str | None = None
    description: str | None = None
    price: int | None = None
    brand_id: int | None = None
    category_id: int | None = None
