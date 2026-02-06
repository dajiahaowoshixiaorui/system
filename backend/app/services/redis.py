"""Redis缓存服务"""
import json
from typing import Optional, Any
from datetime import timedelta
import redis.asyncio as redis
from app.config import settings


class RedisService:
    """Redis缓存服务"""

    _pool = None

    @classmethod
    async def get_pool(cls):
        """获取连接池"""
        if cls._pool is None:
            cls._pool = redis.ConnectionPool(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
                max_connections=20
            )
        return cls._pool

    @classmethod
    async def get_client(cls) -> redis.Redis:
        """获取Redis客户端"""
        pool = await cls.get_pool()
        return redis.Redis(connection_pool=pool)

    @classmethod
    async def get(cls, key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            client = await cls.get_client()
            value = await client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception:
            return None

    @classmethod
    async def set(
        cls,
        key: str,
        value: Any,
        expire: int = 300  # 默认5分钟
    ) -> bool:
        """设置缓存"""
        try:
            client = await cls.get_client()
            await client.setex(key, expire, json.dumps(value, ensure_ascii=False))
            return True
        except Exception:
            return False

    @classmethod
    async def delete(cls, key: str) -> bool:
        """删除缓存"""
        try:
            client = await cls.get_client()
            await client.delete(key)
            return True
        except Exception:
            return False

    @classmethod
    async def delete_pattern(cls, pattern: str) -> int:
        """批量删除缓存"""
        try:
            client = await cls.get_client()
            keys = await client.keys(pattern)
            if keys:
                await client.delete(*keys)
            return len(keys)
        except Exception:
            return 0

    @classmethod
    async def incr(cls, key: str) -> int:
        """递增"""
        try:
            client = await cls.get_client()
            return await client.incr(key)
        except Exception:
            return 0

    @classmethod
    async def decr(cls, key: str) -> int:
        """递减"""
        try:
            client = await cls.get_client()
            return await client.decr(key)
        except Exception:
            return 0

    @classmethod
    async def setnx(cls, key: str, value: Any, expire: int = 300) -> bool:
        """分布式锁"""
        try:
            client = await cls.get_client()
            result = await client.setnx(key, json.dumps(value))
            if result:
                await client.expire(key, expire)
            return bool(result)
        except Exception:
            return False

    @classmethod
    async def hset(cls, name: str, key: str, value: Any) -> bool:
        """Hash设置"""
        try:
            client = await cls.get_client()
            await client.hset(name, key, json.dumps(value))
            return True
        except Exception:
            return False

    @classmethod
    async def hget(cls, name: str, key: str) -> Optional[Any]:
        """Hash获取"""
        try:
            client = await cls.get_client()
            value = await client.hget(name, key)
            if value:
                return json.loads(value)
            return None
        except Exception:
            return None

    @classmethod
    async def hgetall(cls, name: str) -> dict:
        """Hash获取全部"""
        try:
            client = await cls.get_client()
            result = await client.hgetall(name)
            return {k: json.loads(v) for k, v in result.items()}
        except Exception:
            return {}

    @classmethod
    async def expire(cls, key: str, seconds: int) -> bool:
        """设置过期时间"""
        try:
            client = await cls.get_client()
            await client.expire(key, seconds)
            return True
        except Exception:
            return False

    @classmethod
    async def ttl(cls, key: str) -> int:
        """获取剩余过期时间"""
        try:
            client = await cls.get_client()
            return await client.ttl(key)
        except Exception:
            return -2
