from fastapi import APIRouter

from api.routs import brand, category

api_router = APIRouter()
api_router.include_router(brand.router)
api_router.include_router(category.router)
