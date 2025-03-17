from typing import Annotated
from fastapi import HTTPException, UploadFile, status
from pydantic import BeforeValidator, Field
import os, uuid

import config


def generate_unique_filename(filename: str, max_length: int = 255):
    unique_id = uuid.uuid4().hex

    name, ext = os.path.splitext(filename)

    uuid_length = len(unique_id) + 1  # +1 для символа "_"
    ext_length = len(ext)
    max_name_length = max_length - uuid_length - ext_length

    if len(name) > max_name_length:
        name = name[:max_name_length]  # Обрезаем имя до max_name_length символов

    unique_name = f"{name}_{unique_id}{ext}"
    return unique_name


# Функция для валидации типа файла
def validate_file_type(file: UploadFile):
    if not file.content_type.startswith(config.ALLOWED_MIME_TYPE):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not allowed. Only images are allowed."
        )
    return file


# Функция для валидации размера файла
def validate_file_size(file: UploadFile):
    if file.size > config.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the maximum allowed size (5 MB)."
        )
    return file


# Кастомный тип с валидаторами
ImageFile = Annotated[
    UploadFile,
    BeforeValidator(validate_file_type),
    BeforeValidator(validate_file_size),
    Field(description="Only image files less than 5 MB are allowed.")
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
