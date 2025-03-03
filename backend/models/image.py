from sqlmodel import Field, SQLModel


class ImageBase(SQLModel):
    name: str = Field(index=True, max_length=255)


class Image(ImageBase, table=True):
    id: int = Field(default=None, primary_key=True)


class ImagePublic(ImageBase):
    name: str

'''
class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    name: str | None = None
'''
