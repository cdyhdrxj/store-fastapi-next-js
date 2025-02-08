from fastapi import FastAPI
from api.main import api_router

from db import create_db_and_tables

app = FastAPI()

app.include_router(api_router)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()