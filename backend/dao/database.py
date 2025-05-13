import asyncpg
from typing import Optional
from utils.config_utils import get_postgresql_config

class Database:
    _pool: Optional[asyncpg.Pool] = None

    @classmethod
    async def get_pool(cls) -> asyncpg.Pool:
        """获取数据库连接池"""
        if cls._pool is None:
            config = get_postgresql_config()
            try:
                cls._pool = await asyncpg.create_pool(
                    user=config['user'],
                    password=config['password'],
                    database=config['database'],
                    host=config['host'],
                    port=config['port'],
                    min_size=5,
                    max_size=20
                )
            except Exception as e:
                raise Exception(f"无法创建数据库连接池: {str(e)}")
        return cls._pool

    @classmethod
    async def close_pool(cls):
        """关闭数据库连接池"""
        if cls._pool:
            await cls._pool.close()
            cls._pool = None 