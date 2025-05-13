from typing import Tuple, List, Dict, Any, Optional
import asyncpg
from langchain_core.messages import BaseMessage
from dao.message_dao import ChatHistoryDAO, ChatMessageHistory, MessageDAO

class MessageService:
    """消息服务，提供消息和聊天历史相关的业务逻辑"""
    
    @staticmethod
    async def get_chat_history(topic_id: Optional[str] = None, user_id: Optional[int] = None) -> Tuple[ChatMessageHistory, asyncpg.Connection]:
        """获取聊天历史记录
        
        Args:
            topic_id: 话题ID，如果为None则创建新会话
            user_id: 用户ID，如果为None则使用系统用户ID
            
        Returns:
            Tuple[ChatMessageHistory, asyncpg.Connection]: 聊天历史对象和数据库连接
        """
        # 确保ID是整数类型
        user_id = int(user_id) if isinstance(user_id, str) else user_id
        topic_id = int(topic_id) if isinstance(topic_id, str) else topic_id
        
        return await ChatHistoryDAO.get_chat_history(topic_id, user_id)
    
    @staticmethod
    async def release_connection(connection: asyncpg.Connection) -> None:
        """释放数据库连接
        
        Args:
            connection: 数据库连接
        """
        await ChatHistoryDAO.release_connection(connection)
    
    @staticmethod
    async def create_message(topic_id: int, user_id: int, message_type: str, content: str) -> Dict[str, Any]:
        """创建新消息
        
        Args:
            topic_id: 话题ID
            user_id: 用户ID
            message_type: 消息类型 ('user' 或 'ai')
            content: 消息内容
            
        Returns:
            Dict[str, Any]: 创建的消息信息
        """
        return await MessageDAO.create_message(topic_id, user_id, message_type, content)
    
    @staticmethod
    async def get_topic_messages(topic_id: int) -> List[Dict[str, Any]]:
        """获取话题的所有消息
        
        Args:
            topic_id: 话题ID
            
        Returns:
            List[Dict[str, Any]]: 话题的所有消息
        """
        return await MessageDAO.get_topic_messages(topic_id)
    
    @staticmethod
    async def get_latest_messages(topic_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """获取话题的最新消息
        
        Args:
            topic_id: 话题ID
            limit: 限制返回的消息数量
            
        Returns:
            List[Dict[str, Any]]: 话题的最新消息
        """
        return await MessageDAO.get_latest_messages(topic_id, limit)
    
    @staticmethod
    async def add_message_to_history(history: ChatMessageHistory, message: BaseMessage) -> None:
        """向聊天历史添加消息
        
        Args:
            history: 聊天历史对象
            message: 要添加的消息
        """
        await history.add_message(message)
    
    @staticmethod
    async def add_user_message_to_history(history: ChatMessageHistory, content: str) -> None:
        """向聊天历史添加用户消息
        
        Args:
            history: 聊天历史对象
            content: 消息内容
        """
        await history.add_user_message(content)
    
    @staticmethod
    async def add_ai_message_to_history(history: ChatMessageHistory, content: str) -> None:
        """向聊天历史添加AI消息
        
        Args:
            history: 聊天历史对象
            content: 消息内容
        """
        await history.add_ai_message(content)
    
    @staticmethod
    async def get_history_messages(history: ChatMessageHistory) -> List[BaseMessage]:
        """获取聊天历史中的所有消息
        
        Args:
            history: 聊天历史对象
            
        Returns:
            List[BaseMessage]: 聊天历史中的所有消息
        """
        return await history.get_messages()
    
    @staticmethod
    async def stream_process_user_message(user_message: str, topic_id: str, user_info: Dict[str, Any], user_id: int = None):
        """
        以流的方式处理用户消息，返回AI响应的生成器
        
        Args:
            user_message: 用户消息
            topic_id: 话题ID
            user_info: 用户信息（省份、分数、科目等）
            user_id: 用户ID，必须提供
            
        Returns:
            异步生成器: 产生JSON格式的响应，包含内容类型和内容
            
        Raises:
            ValueError: 如果未提供user_id
        """
        if not user_id:
            raise ValueError("必须提供用户ID")
        
        from graph.graph import getGraph
        import json
        
        # 从数据库获取聊天历史记录并放入state中
        print("topic_id", topic_id, "user_id", user_id)
        chat_history, connection = await MessageService.get_chat_history(topic_id, user_id)
        history_messages = await MessageService.get_history_messages(chat_history)
        # 拼接用户消息
        history_messages.append({"role": "user", "content": user_message})
        inputs = {
            "messages": history_messages,
            "user_info": user_info,
            "intent": None
        }
        
        # 确保这里的配置一定包含user_id
        config = {
            "configurable": {
                "topic_id": topic_id,
                "user_id": user_id  
            }
        }
        
        # 获取图谱并调用流式处理
        graph = getGraph()
        
        # 使用流式模式获取结果
        for msg, metadata in graph.stream(
            inputs, 
            config,
            stream_mode="messages"
        ):
            if metadata and metadata.get("langgraph_node") in ["recommender", "chitchat"]:
                if msg.additional_kwargs and msg.additional_kwargs.get("reasoning_content"):
                    reasoning_content = msg.additional_kwargs.get("reasoning_content")
                    if reasoning_content and reasoning_content.strip():
                        yield f"data: {json.dumps({'content': reasoning_content, 'type': 'reasoning'},ensure_ascii=False)}\n\n" 
                elif msg.content:
                    yield f"data: {json.dumps({'content': msg.content, 'type': 'answer'}, ensure_ascii=False)}\n\n"
        
        # 释放数据库连接
        await MessageService.release_connection(connection)
    
    @staticmethod
    async def clear_history(history: ChatMessageHistory) -> None:
        """清除聊天历史
        
        Args:
            history: 聊天历史对象
        """
        await history.clear() 