from typing import Annotated
from fastapi import HTTPException, UploadFile, status
from pydantic import BeforeValidator, Field
import os, uuid

import config


def generate_unique_filename(filename: str, max_length: int = 255):
    unique_id = uuid.uuid4().hex

    name, ext = os.path.splitext(filename)

    unique_name = f"{name}_{unique_id}{ext}"
    if len(unique_id) > max_length:
        unique_name = unique_name[-max_length:]
    return unique_name


# Функция для валидации типа файла
def validate_file_type(file: UploadFile):
    if not file.content_type.startswith(config.ALLOWED_MIME_TYPE):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл не является изображением"
        )
    return file


# Функция для валидации размера файла
def validate_file_size(file: UploadFile):
    if file.size > config.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Размер файла более 5 МБ"
        )
    return file


# Кастомный тип с валидаторами
ImageFile = Annotated[
    UploadFile,
    BeforeValidator(validate_file_type),
    BeforeValidator(validate_file_size),
    Field(description="Разрешены только изображения размером не более 5 МБ")
]


def image_upload(file: ImageFile):
    try:
        # Генерируем уникальное имя файла
        unique_filename = generate_unique_filename(file.filename)
        file_path = os.path.join(config.UPLOAD_FOLDER, unique_filename)
        
        # Сохраняем файл
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())
        
        return unique_filename
    except Exception as e:
        return None


def image_delete(filename: str):
    file_path = os.path.join(config.UPLOAD_FOLDER, filename)

    try:
        os.remove(file_path)
        return True
    except Exception as e:
        return False
