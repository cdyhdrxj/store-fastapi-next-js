from passlib.context import CryptContext
from sqlmodel import select

from models.user import User, UserLogin
from api.deps import SessionDep

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)

def read_user_by_username(username: str, session: SessionDep) -> UserLogin:
    user_db = session.exec(select(User).where(User.username == username)).first()
    if not user_db:
        return None
    return UserLogin.model_validate(user_db)
