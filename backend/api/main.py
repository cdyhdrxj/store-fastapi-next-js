from fastapi import APIRouter

from api.routs import brand, category, item, image

api_router = APIRouter()
api_router.include_router(brand.router)
api_router.include_router(category.router)
api_router.include_router(item.router)
api_router.include_router(image.router)
