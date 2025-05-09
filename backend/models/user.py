from enum import Enum
from sqlmodel import SQLModel, Field

class Role(str, Enum):
    USER = "user"
    MANAGER = "manager"
    ADMIN = "admin"


class UserBase(SQLModel):
    username: str = Field(min_length=3, max_length=64, unique=True)
    role: Role


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    password_hash: str | None = None


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=64)


class UserRead(UserBase):
    id: int


class UserLogin(UserRead):
    password_hash: str


class UserToken(UserBase):
    pass


class UserUpdate(SQLModel):
    role: Role