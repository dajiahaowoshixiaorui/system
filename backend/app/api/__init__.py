"""API路由包"""
from app.api.auth import router as auth_router
from app.api.books import router as books_router
from app.api.categories import router as categories_router
from app.api.borrows import router as borrows_router
from app.api.users import router as users_router

__all__ = [
    "auth_router",
    "books_router",
    "categories_router",
    "borrows_router",
    "users_router",
]
