"""认证中间件"""
from typing import Optional
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.api.auth import decode_token


class AuthMiddleware(BaseHTTPMiddleware):
    """认证中间件"""

    # 公开路由（不需要认证）
    PUBLIC_PATHS = [
        "/",
        "/health",
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/docs",
        "/redoc",
        "/openapi.json",
    ]

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # 检查是否公开路由
        path = request.url.path
        if self._is_public_path(path):
            return await call_next(request)

        # 从Header获取Token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            # 允许OPTIONS请求（跨域预检）
            if request.method == "OPTIONS":
                return await call_next(request)
            return JSONResponse(
                status_code=401,
                content={"code": 401, "status": "error", "message": "缺少认证令牌"}
            )

        token = auth_header.split(" ")[1]
        token_data = decode_token(token)

        if not token_data:
            return JSONResponse(
                status_code=401,
                content={"code": 401, "status": "error", "message": "无效或已过期"}
            )

        # 将用户信息注入请求状态
        request.state.user = token_data

        return await call_next(request)

    def _is_public_path(self, path: str) -> bool:
        """检查是否是公开路由"""
        for public_path in self.PUBLIC_PATHS:
            if path.startswith(public_path):
                return True
        return False


class CORSMiddleware(BaseHTTPMiddleware):
    """CORS中间件"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # 添加CORS头
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"

        return response
