from sqlmodel import Field, SQLModel


class CoverBase(SQLModel):
    name: str = Field(min_length=1, max_length=255, unique=True)


class Cover(CoverBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class CoverRead(CoverBase):
    id: int
