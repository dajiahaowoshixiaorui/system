"""Pydantic模式包"""
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserLogin
from app.schemas.book import BookCreate, BookUpdate, BookResponse, BookQuery
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.schemas.borrow import BorrowCreate, BorrowResponse, BorrowQuery, ReturnBook
from app.schemas.common import Token, TokenData, ResponseModel, PaginatedResponse

__all__ = [
    "UserCreate", "UserUpdate", "UserResponse", "UserLogin",
    "BookCreate", "BookUpdate", "BookResponse", "BookQuery",
    "CategoryCreate", "CategoryUpdate", "CategoryResponse",
    "BorrowCreate", "BorrowResponse", "BorrowQuery", "ReturnBook",
    "Token", "TokenData", "ResponseModel", "PaginatedResponse",
]
