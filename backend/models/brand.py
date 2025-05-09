from sqlmodel import Field, SQLModel


class BrandBase(SQLModel):
    name: str = Field(min_length=1, max_length=50)


class Brand(BrandBase, table=True):
    id: int | None = Field(None, primary_key=True)


class BrandRead(BrandBase):
    id: int


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BrandBase):
    name: str | None = Field(None, min_length=1, max_length=50)
