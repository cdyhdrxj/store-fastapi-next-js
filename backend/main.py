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
    allow_credentials=True,  # Для httponly cookie
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)
app.include_router(api_router)

create_db_and_tables()
