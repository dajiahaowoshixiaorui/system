"""FastAPI应用入口"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.api import (
    auth_router,
    books_router,
    categories_router,
    borrows_router,
    users_router,
)
from app.middleware.auth import AuthMiddleware
from app.services.search import SearchService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print("Starting Library Management System...")

    # 初始化数据库
    init_db()
    print("Database initialized")

    # 初始化Elasticsearch索引
    try:
        SearchService.init_index()
        print("Elasticsearch index initialized")
    except Exception as e:
        print(f"Elasticsearch init warning: {e}")

    # 创建上传目录
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    yield

    # 关闭时
    print("Shutting down...")


# 创建FastAPI应用
app = FastAPI(
    title="图书管理系统 API",
    description="功能完善的图书管理系统后端API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加认证中间件
app.add_middleware(AuthMiddleware)

# 挂载静态文件目录
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# 注册路由
app.include_router(auth_router, prefix="/api/v1")
app.include_router(books_router, prefix="/api/v1")
app.include_router(categories_router, prefix="/api/v1")
app.include_router(borrows_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "图书管理系统 API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
    )
