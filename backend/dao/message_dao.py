from typing import Optional, Dict, Any, List, Tuple
import asyncpg
from .database import Database
import uuid
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain.schema import BaseChatMessageHistory
from utils.format_utils import format_datetime, format_datetime_list

class MessageDAO:
    @staticmethod
    async def create_message(topic_id: int, user_id: int, message_type: str, content: str) -> Dict[str, Any]:
        """创建新消息"""
        pool = await Database.get_pool()
        async with pool.acquire() as conn:
            try:
                # 开始事务
                async with conn.transaction():
                    # 插入新消息
                    result = await conn.fetchrow(
                        """
                        INSERT INTO messages (topic_id, user_id, message_type, content)
                        VALUES ($1, $2, $3, $4)
                        RETURNING message_id, topic_id, user_id, message_type, content, created_at
                        """,
                        topic_id, user_id, message_type, content
                    )
                    
                    # 更新话题的updated_at时间戳
                    await conn.execute(
                        """
                        UPDATE topics
                        SET updated_at = CURRENT_TIMESTAMP
                        WHERE topic_id = $1
                        """,
                        topic_id
                    )
                    
                    return format_datetime(dict(result))
            except asyncpg.ForeignKeyViolationError:
                raise ValueError("话题ID或用户ID不存在")

    @staticmethod
    async def get_topic_messages(topic_id: int) -> List[Dict[str, Any]]:
        """获取话题的所有消息"""
        pool = await Database.get_pool()
        async with pool.acquire() as conn:
            messages = await conn.fetch(
                """
                SELECT message_id, topic_id, user_id, message_type, content, created_at
                FROM messages
                WHERE topic_id = $1
                ORDER BY created_at ASC
                """,
                topic_id
            )
            return format_datetime_list([dict(message) for message in messages])

    @staticmethod
    async def get_latest_messages(topic_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """获取话题的最新消息"""
        pool = await Database.get_pool()
        async with pool.acquire() as conn:
            messages = await conn.fetch(
                """
                SELECT message_id, topic_id, user_id, message_type, content, created_at
                FROM messages
                WHERE topic_id = $1
                ORDER BY created_at DESC
                LIMIT $2
                """,
                topic_id, limit
            )
            return format_datetime_list([dict(message) for message in messages])

# 聊天历史记录类
class ChatMessageHistory(BaseChatMessageHistory):
    """聊天历史记录类，实现LangChain的BaseChatMessageHistory接口"""
    
    def __init__(self, topic_id: str, connection: asyncpg.Connection, user_id: int = None) -> None:
        """初始化聊天历史
        
        Args:
            topic_id: 话题ID
            connection: 数据库连接
            user_id: 用户ID，默认为None
        """
        # 正确处理topic_id：如果是数字则转为int类型，否则保持字符串格式
        self.topic_id = topic_id  # 保存原始session_id，用于创建新话题时使用
        self.connection = connection
        self.user_id = user_id
    
    async def add_message(self, message: BaseMessage) -> None:
        """添加一条消息到历史记录中"""
        if not self.user_id:
            raise ValueError("无效的用户ID，请确保用户已登录")
            
        if not self.topic_id:
            raise ValueError("无效的topic ID，请确保传入topic_id")

        
        # 确定消息类型
        message_type = "user" if isinstance(message, HumanMessage) else "ai"
        
        # 使用事务同时更新消息和话题的updated_at
        async with self.connection.transaction():
            # 插入消息
            await self.connection.execute(
                """
                INSERT INTO messages (topic_id, user_id, message_type, content)
                VALUES ($1, $2, $3, $4)
                """,
                self.topic_id, self.user_id, message_type, message.content
            )
            
            # 更新话题的updated_at时间戳
            await self.connection.execute(
                """
                UPDATE topics
                SET updated_at = CURRENT_TIMESTAMP
                WHERE topic_id = $1
                """,
                self.topic_id
            )
    
    async def add_user_message(self, text: str) -> None:
        """添加用户消息"""
        await self.add_message(HumanMessage(content=text))
    
    async def add_ai_message(self, text: str) -> None:
        """添加AI消息"""
        await self.add_message(AIMessage(content=text))
    
    async def get_messages(self) -> List[BaseMessage]:
        """获取当前会话所有消息"""
        if not self.topic_id:
            return []
        
        records = await self.connection.fetch(
            """
            SELECT message_type, content 
            FROM messages 
            WHERE topic_id = $1 
            ORDER BY message_id
            """,
            self.topic_id
        )
        
        if not records:
            return []
        
        messages = []
        for record in records:
            if record["message_type"] == "user":
                messages.append(HumanMessage(content=record["content"]))
            else:
                messages.append(AIMessage(content=record["content"]))
        
        return messages
    
    async def clear(self) -> None:
        """清除当前会话的所有消息"""
        if not self.topic_id:
            return
        
        await self.connection.execute(
            "DELETE FROM messages WHERE topic_id = $1",
            self.topic_id
        )

# 聊天历史管理类
class ChatHistoryDAO:
    @staticmethod
    async def get_chat_history(topic_id=None, user_id=None) -> Tuple[ChatMessageHistory, asyncpg.Connection]:
        """初始化聊天历史，返回历史对象和数据库连接
        
        Args:
            topic_id: 话题ID，如果为None则创建新会话
            user_id: 用户ID，必须提供
            
        Returns:
            Tuple[ChatMessageHistory, asyncpg.Connection]: 聊天历史对象和数据库连接
            
        Raises:
            ValueError: 如果未提供用户ID
        """
        if user_id is None:
            raise ValueError("必须提供用户ID")
            
        if topic_id is None:
            topic_id = str(uuid.uuid4())
        
        pool = await Database.get_pool()
        connection = await pool.acquire()
        
        history = ChatMessageHistory(
            topic_id=topic_id,
            connection=connection,
            user_id=user_id
        )
        
        return history, connection
    
    @staticmethod
    async def release_connection(connection: asyncpg.Connection):
        """释放数据库连接回连接池"""
        pool = await Database.get_pool()
        await pool.release(connection) 