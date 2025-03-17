from fastapi import APIRouter

from api.routs import brand, category, item, cover, images, user, login

api_router = APIRouter()
api_router.include_router(brand.router)
api_router.include_router(category.router)
api_router.include_router(item.router)
api_router.include_router(cover.router)
api_router.include_router(images.router)
api_router.include_router(user.router)
api_router.include_router(login.router)
