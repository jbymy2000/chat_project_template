from typing import Optional, Dict, Any, List
import asyncpg
from .database import Database
from datetime import datetime
from utils.format_utils import format_datetime, format_datetime_list

class TopicDAO:
    @staticmethod
    async def create_topic(user_id: int, topic: str) -> Dict[str, Any]:
        """创建新话题"""
        pool = await Database.get_pool()
        async with pool.acquire() as conn:
            try:
                result = await conn.fetchrow(
                    """
                    INSERT INTO topics (user_id, topic)
                    VALUES ($1, $2)
                    RETURNING topic_id, user_id, topic, started_at, updated_at
                    """,
                    user_id, topic
                )
                return format_datetime(dict(result))
            except asyncpg.ForeignKeyViolationError:
                raise ValueError("用户ID不存在")

    @staticmethod
    async def get_user_topics(user_id: int) -> List[Dict[str, Any]]:
        """获取用户的所有话题"""
        pool = await Database.get_pool()
        async with pool.acquire() as conn:
            topics = await conn.fetch(
                """
                SELECT topic_id, user_id, topic, started_at, updated_at
                FROM topics
                WHERE user_id = $1
                ORDER BY updated_at DESC
                """,
                user_id
            )
            return format_datetime_list([dict(topic) for topic in topics])

    @staticmethod
    async def update_topic(topic_id: int, topic: str) -> Optional[Dict[str, Any]]:
        """更新话题"""
        pool = await Database.get_pool()
        async with pool.acquire() as conn:
            result = await conn.fetchrow(
                """
                UPDATE topics
                SET topic = $2, updated_at = $3
                WHERE topic_id = $1
                RETURNING topic_id, user_id, topic, started_at, updated_at
                """,
                topic_id, topic, datetime.now()
            )
            return format_datetime(dict(result)) if result else None 