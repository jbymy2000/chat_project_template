from typing import Optional, Dict, Any
import asyncpg
from .database import Database
from datetime import datetime
from utils.format_utils import format_datetime

class AuthDAO:
    @staticmethod
    async def create_user(username: str, password_hash: str, email: Optional[str] = None, 
                         phone_number: Optional[str] = None) -> Dict[str, Any]:
        """创建新用户"""
        pool = await Database.get_pool()
        async with pool.acquire() as conn:
            try:
                user = await conn.fetchrow(
                    """
                    INSERT INTO auth_users (username, password_hash, email, phone_number)
                    VALUES ($1, $2, $3, $4)
                    RETURNING user_id, username, email, phone_number, created_at
                    """,
                    username, password_hash, email, phone_number
                )
                return format_datetime(dict(user))
            except asyncpg.UniqueViolationError:
                raise ValueError("用户名、邮箱或手机号已存在")

    @staticmethod
    async def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
        """通过用户名获取用户信息"""
        pool = await Database.get_pool()
        async with pool.acquire() as conn:
            user = await conn.fetchrow(
                """
                SELECT user_id, username, password_hash, email, phone_number, created_at, updated_at
                FROM auth_users
                WHERE username = $1
                """,
                username
            )
            return format_datetime(dict(user)) if user else None

    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """通过用户ID获取用户信息"""
        pool = await Database.get_pool()
        async with pool.acquire() as conn:
            user = await conn.fetchrow(
                """
                SELECT user_id, username, password_hash, email, phone_number, created_at, updated_at
                FROM auth_users
                WHERE user_id = $1
                """,
                user_id
            )
            return format_datetime(dict(user)) if user else None

    @staticmethod
    async def update_user(user_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """更新用户信息"""
        pool = await Database.get_pool()
        async with pool.acquire() as conn:
            # 构建更新字段
            update_fields = []
            values = []
            for key, value in kwargs.items():
                if value is not None and key in ['email', 'phone_number', 'password_hash']:
                    update_fields.append(f"{key} = ${len(values) + 2}")
                    values.append(value)
            
            if not update_fields:
                return None

            update_fields.append("updated_at = $" + str(len(values) + 2))
            values.append(datetime.now())

            query = f"""
                UPDATE auth_users
                SET {', '.join(update_fields)}
                WHERE user_id = $1
                RETURNING user_id, username, email, phone_number, updated_at
            """
            values.insert(0, user_id)
            
            try:
                user = await conn.fetchrow(query, *values)
                return format_datetime(dict(user)) if user else None
            except asyncpg.UniqueViolationError:
                raise ValueError("邮箱或手机号已被使用") 