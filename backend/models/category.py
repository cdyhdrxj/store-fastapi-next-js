from sqlmodel import Field, SQLModel


class CategoryBase(SQLModel):
    name: str = Field(index=True, max_length=50)


class Category(CategoryBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class CategoryPublic(CategoryBase):
    id: int


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    name: str | None = None
