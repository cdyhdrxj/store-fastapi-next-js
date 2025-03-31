from sqlmodel import Field, SQLModel, Relationship

from models.brand import Brand, BrandRead
from models.category import Category, CategoryRead
from models.cover import Cover, CoverRead


class ItemBase(SQLModel):
    name: str = Field(max_length=50)
    description: str = Field(max_length=200)
    price: int = Field(ge=0, le=10 ** 8)


class Item(ItemBase, table=True):
    id: int | None = Field(None, primary_key=True)
    brand_id: int = Field(foreign_key="brand.id", ondelete="RESTRICT")
    category_id: int = Field(foreign_key="category.id", ondelete="RESTRICT")
    cover_id: int | None = Field(None, foreign_key="cover.id", ondelete="SET NULL")
    quantity: int | None = Field(0, ge=0, le=10 ** 8)
    brand: Brand | None = Relationship()
    category: Category | None = Relationship()
    cover: Cover | None = Relationship()

    images: list["Image"] = Relationship(back_populates="item")

    # desc2: str = Field(max_length=200)


class ItemRead(ItemBase):
    id: int
    brand: BrandRead = None
    category: CategoryRead = None
    cover: CoverRead | None = None
    quantity: int

    # desc2: str | None = None


class ItemReadImages(ItemRead):
    images: list["ImageRead"] = []


class ItemCreate(ItemBase):
    brand_id: int
    category_id: int


class ItemUpdate(ItemBase):
    name: str | None = Field(None, max_length=50)
    description: str | None = Field(None, max_length=200)
    price: int | None = Field(None, ge=0, le=10 ** 8)
    brand_id: int | None = None
    category_id: int | None = None


class CoverUpdate(ItemUpdate):
    cover_id: int | None = None


class ItemAdd(SQLModel):
    quantity: int


# -------------------------------------------------------------------
# Классы, связанные с картинками (не знаю, как развести их в разные файлы)
# -------------------------------------------------------------------
class ImageBase(SQLModel):
    name: str = Field(max_length=255)


class Image(ImageBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    item_id: int = Field(foreign_key="item.id")
    item: Item = Relationship(back_populates="images")


class ImageRead(ImageBase):
    id: int


class ImageCreate(ImageBase):
    item_id: int
# -------------------------------------------------------------------
