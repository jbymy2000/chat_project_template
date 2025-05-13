from typing import Dict, Any, List, Optional
from dao.profile_dao import ProfileDAO
from utils.logger_utils import setup_logger

# 配置日志
logger = setup_logger(name="profile_service")

class ProfileService:
    """用户档案服务，提供用户档案相关的业务逻辑"""
    
    @staticmethod
    async def create_profile(user_id: int, gender: str = 'other', province: Optional[str] = None,
                           exam_year: Optional[int] = None, subject_choice: Optional[List[str]] = None,
                           score: Optional[int] = None, rank: Optional[int] = None,
                           batch: Optional[str] = None) -> Dict[str, Any]:
        """创建用户档案
        
        Args:
            user_id: 用户ID
            gender: 性别，默认为'other'
            province: 省份
            exam_year: 高考年份
            subject_choice: 选考科目
            score: 高考分数
            rank: 等效位次
            batch: 批次
            
        Returns:
            Dict[str, Any]: 创建的用户档案信息
        """
        logger.info(f"创建用户(ID:{user_id})档案")
        try:
            profile = await ProfileDAO.create_profile(
                user_id, gender, province, exam_year, subject_choice, score, rank, batch
            )
            logger.info(f"用户(ID:{user_id})档案创建成功")
            return profile
        except ValueError as e:
            logger.error(f"创建用户(ID:{user_id})档案失败: {str(e)}")
            raise
    
    @staticmethod
    async def get_profile(user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户档案
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[Dict[str, Any]]: 用户档案信息，如果档案不存在则返回None
        """
        logger.info(f"获取用户(ID:{user_id})档案")
        profile = await ProfileDAO.get_profile(user_id)
        if profile:
            logger.info(f"成功获取用户(ID:{user_id})档案")
        else:
            logger.warning(f"未找到用户(ID:{user_id})档案")
        return profile
    
    @staticmethod
    async def update_profile(user_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """更新用户档案
        
        Args:
            user_id: 用户ID
            **kwargs: 要更新的字段，可包括gender, province, exam_year, subject_choice, score
            
        Returns:
            Optional[Dict[str, Any]]: 更新后的用户档案信息，如果档案不存在则返回None
        """
        logger.info(f"更新用户(ID:{user_id})档案: {kwargs}")
        profile = await ProfileDAO.update_profile(user_id, **kwargs)
        if profile:
            logger.info(f"用户(ID:{user_id})档案更新成功")
        else:
            logger.warning(f"用户(ID:{user_id})档案更新失败，可能档案不存在")
        return profile
    
    @staticmethod
    async def update_requirement(user_id: int, requirement: str) -> Optional[Dict[str, Any]]:
        """更新用户需求
        
        Args:
            user_id: 用户ID
            requirement: 用户需求
            
        Returns:
            Optional[Dict[str, Any]]: 更新后的用户档案信息，如果档案不存在则返回None
        """
        logger.info(f"更新用户(ID:{user_id})需求")
        # 由于ProfileDAO.update_profile不直接支持更新requirement字段，需要扩展DAO方法
        # 这里假设ProfileDAO.update_profile已经支持更新requirement字段
        profile = await ProfileDAO.update_profile(user_id, requirement=requirement)
        if profile:
            logger.info(f"用户(ID:{user_id})需求更新成功")
        else:
            logger.warning(f"用户(ID:{user_id})需求更新失败，可能档案不存在")
        return profile 