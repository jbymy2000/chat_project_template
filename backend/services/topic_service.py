from typing import List, Dict, Any, Optional
from dao.topic_dao import TopicDAO
from services.message_service import MessageService
from graph.text_captioning import generate_text_caption
from utils.logger_utils import setup_logger

# 配置日志
logger = setup_logger(name="topic_service")

class TopicService:
    """话题服务，提供话题相关的业务逻辑"""
    
    @staticmethod
    async def generate_topic_caption(text: str) -> str:
        """为用户提问生成话题名称摘要
        
        Args:
            text: 用户提问的原始文本
            
        Returns:
            str: 生成的话题名称摘要
        """
        logger.info(f"为用户问题生成话题名称摘要: {text}")
        try:
            # 生成文本摘要作为话题名称
            caption_result = generate_text_caption(text)
            topic_name = caption_result["caption"]
            
            # 检查生成的摘要是否有效
            if not topic_name or len(topic_name.strip()) == 0:
                logger.warning(f"生成的话题名称为空，使用原始问题: {text}")
                topic_name = text[:20] + "..." if len(text) > 20 else text
            
            logger.info(f"生成的话题名称: {topic_name}")
            return topic_name
        except Exception as e:
            logger.error(f"生成话题名称时出错: {str(e)}")
            # 如果生成失败，使用原始问题的前20个字符作为话题名称
            return text[:20] + "..." if len(text) > 20 else text
    
    @staticmethod
    async def create_topic_with_caption(user_id: int, question: str, use_caption: bool = True) -> Dict[str, Any]:
        """创建新话题并自动生成话题名称
        
        Args:
            user_id: 用户ID
            question: 用户原始问题
            use_caption: 是否使用文本摘要生成话题名称
            
        Returns:
            Dict[str, Any]: 创建的话题信息
        """
        # 生成话题名称
        topic_name = question
        if use_caption:
            topic_name = await TopicService.generate_topic_caption(question)
        
        # 创建话题
        return await TopicService.create_topic(user_id, topic_name, question)
    
    @staticmethod
    async def create_topic(user_id: int, topic: str, original_question: str = None) -> Dict[str, Any]:
        """创建新话题
        
        Args:
            user_id: 用户ID
            topic: 话题名称（可能是自动生成的摘要）
            original_question: 用户原始问题，如果不为None，会创建第一条消息
            
        Returns:
            Dict[str, Any]: 创建的话题信息
        """
        # 创建话题
        new_topic = await TopicDAO.create_topic(user_id, topic)
        return new_topic
    
    @staticmethod
    async def get_user_topics(user_id: int) -> List[Dict[str, Any]]:
        """获取用户的所有话题
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[Dict[str, Any]]: 用户的所有话题
        """
        return await TopicDAO.get_user_topics(user_id)
    
    @staticmethod
    async def update_topic(topic_id: int, topic: str) -> Optional[Dict[str, Any]]:
        """更新话题
        
        Args:
            topic_id: 话题ID
            topic: 新的话题名称
            
        Returns:
            Optional[Dict[str, Any]]: 更新后的话题信息，如果话题不存在则返回None
        """
        return await TopicDAO.update_topic(topic_id, topic) 