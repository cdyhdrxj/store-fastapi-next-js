from sqlmodel import Field, SQLModel


class CoverBase(SQLModel):
    name: str = Field(max_length=255)


class Cover(CoverBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class CoverRead(CoverBase):
    id: int
