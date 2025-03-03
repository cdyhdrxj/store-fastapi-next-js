from sqlmodel import Session, SQLModel, create_engine, text

from config import SQLITE_FILE_NAME

sqlite_url = f"sqlite:///{SQLITE_FILE_NAME}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    with engine.connect() as connection:
       connection.execute(text("PRAGMA foreign_keys=ON"))  # Только для SQLite


def get_session():
    with Session(engine) as session:
        yield session
