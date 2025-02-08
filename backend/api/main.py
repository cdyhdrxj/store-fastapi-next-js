from fastapi import APIRouter

from api.routs import brand

api_router = APIRouter()
api_router.include_router(brand.router)