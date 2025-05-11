from typing import Annotated
from fastapi import Depends
from sqlmodel import Session

from db import get_session

SessionDep = Annotated[Session, Depends(get_session)]

from general.connection_manager import ConnectionManager

manager = ConnectionManager()
