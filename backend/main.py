from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.main import api_router

from db import create_db_and_tables

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Для разработки
    ],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)
app.include_router(api_router)

create_db_and_tables()
