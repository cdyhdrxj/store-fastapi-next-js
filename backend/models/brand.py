from sqlmodel import Field, SQLModel


class BrandBase(SQLModel):
    name: str = Field(index=True, max_length=50)


class Brand(BrandBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class BrandPublic(BrandBase):
    id: int


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BrandBase):
    name: str | None = None
