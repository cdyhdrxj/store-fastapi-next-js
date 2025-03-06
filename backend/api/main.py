from fastapi import APIRouter

from api.routs import brand, category, item, cover

api_router = APIRouter()
api_router.include_router(brand.router)
api_router.include_router(category.router)
api_router.include_router(item.router)
api_router.include_router(cover.router)
