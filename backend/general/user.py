from sqlmodel import select

from models.user import User, UserLogin
from api.deps import SessionDep

def read_user_by_username(username: str, session: SessionDep) -> UserLogin:
    user_db = session.exec(select(User).where(User.username == username)).first()
    if not user_db:
        return None
    return UserLogin.model_validate(user_db)
