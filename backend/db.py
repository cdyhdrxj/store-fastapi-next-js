from sqlmodel import Session, SQLModel, create_engine, text

from models.user import User, Role
from general.password import get_password_hash
from config import SQLITE_URL

connect_args = {"check_same_thread": False}
engine = create_engine(SQLITE_URL, connect_args=connect_args)

def create_users():
    admin = User(username="admin", role=Role.ADMIN, password_hash=get_password_hash("adminadmin"))
    manager = User(username="manager", role=Role.MANAGER, password_hash=get_password_hash("managermanager"))
    user = User(username="user", role=Role.USER, password_hash=get_password_hash("useruser"))

    session = Session(engine)

    session.add(admin)
    session.add(manager)
    session.add(user)

    session.commit()


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    with engine.connect() as connection:
       connection.execute(text("PRAGMA foreign_keys=ON"))  # Только для SQLite

    # create_users()


def get_session():
    with Session(engine) as session:
        yield session
