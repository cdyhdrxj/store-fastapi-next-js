from sqlmodel import Field, SQLModel


class CategoryBase(SQLModel):
    name: str = Field(max_length=50)


class Category(CategoryBase, table=True):
    id: int | None = Field(None, primary_key=True)


class CategoryRead(CategoryBase):
    id: int


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    name: str | None = Field(None, max_length=50)
