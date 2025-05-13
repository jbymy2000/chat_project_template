from typing import Optional, Dict, Any, List
import asyncpg
from .database import Database
from utils.format_utils import format_datetime

class ProfileDAO:
    @staticmethod
    async def create_profile(user_id: int, gender: str = 'other', province: Optional[str] = None,
                           exam_year: Optional[int] = None, subject_choice: Optional[List[str]] = None,
                           score: Optional[int] = None, rank: Optional[int] = None,
                           batch: Optional[str] = None) -> Dict[str, Any]:
        """创建用户档案"""
        pool = await Database.get_pool()
        async with pool.acquire() as conn:
            try:
                profile = await conn.fetchrow(
                    """
                    INSERT INTO user_profiles (user_id, gender, province, exam_year, subject_choice, score, rank, batch)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    RETURNING user_id, gender, province, exam_year, subject_choice, score, rank, batch, updated_at
                    """,
                    user_id, gender, province, exam_year, subject_choice, score, rank, batch
                )
                return format_datetime(dict(profile))
            except asyncpg.ForeignKeyViolationError:
                raise ValueError("用户ID不存在")
            except asyncpg.UniqueViolationError:
                raise ValueError("用户档案已存在")

    @staticmethod
    async def get_profile(user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户档案"""
        pool = await Database.get_pool()
        async with pool.acquire() as conn:
            profile = await conn.fetchrow(
                """
                SELECT user_id, gender, province, exam_year, subject_choice, score, requirement, rank, batch, updated_at
                FROM user_profiles
                WHERE user_id = $1
                """,
                user_id
            )
            return format_datetime(dict(profile)) if profile else None

    @staticmethod
    async def update_profile(user_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """更新用户档案"""
        pool = await Database.get_pool()
        async with pool.acquire() as conn:
            # 构建更新字段
            update_fields = []
            values = []
            valid_fields = ['gender', 'province', 'exam_year', 'subject_choice', 'score', 'requirement', 'rank', 'batch']
            
            for key, value in kwargs.items():
                if value is not None and key in valid_fields:
                    update_fields.append(f"{key} = ${len(values) + 2}")
                    values.append(value)
            
            if not update_fields:
                return None

            query = f"""
                UPDATE user_profiles
                SET {', '.join(update_fields)}
                WHERE user_id = $1
                RETURNING user_id, gender, province, exam_year, subject_choice, score, requirement, rank, batch, updated_at
            """
            values.insert(0, user_id)
            
            try:
                profile = await conn.fetchrow(query, *values)
                return format_datetime(dict(profile)) if profile else None
            except asyncpg.ForeignKeyViolationError:
                raise ValueError("用户ID不存在") 