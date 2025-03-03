from typing import Annotated
from fastapi import APIRouter, HTTPException, Query
from fastapi import FastAPI, File, UploadFile
from pydantic import BeforeValidator, Field
from sqlmodel import select

from api.deps import SessionDep
import config

import os
import uuid

def generate_unique_filename(filename: str):
    # Генерируем UUID
    unique_id = uuid.uuid4().hex
    # Разделяем имя файла и расширение
    name, ext = os.path.splitext(filename)
    # Создаем уникальное имя
    unique_name = f"{name}_{unique_id}{ext}"
    return unique_name

# Функция для валидации типа файла
def validate_file_type(file: UploadFile):
    if file.content_type not in config.ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="File type not allowed. Only images are allowed.")
    return file

# Функция для валидации размера файла
def validate_file_size(file: UploadFile):
    if file.size > config.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds the maximum allowed size (5 MB).")
    return file

# Кастомный тип с валидаторами
ImageFile = Annotated[
    UploadFile,
    BeforeValidator(validate_file_type),
    BeforeValidator(validate_file_size),
    Field(description="Only image files (JPEG, PNG, GIF) less than 5 MB are allowed.")
]

router = APIRouter(
    prefix="/files",
    tags=["file"],
)

@router.post("/")
def create_file(file: ImageFile):
    # Генерируем уникальное имя файла
    unique_filename = generate_unique_filename(file.filename)
    file_path = os.path.join(config.UPLOAD_FOLDER, unique_filename)
    
    # Сохраняем файл
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    
    return {"path": file_path}
