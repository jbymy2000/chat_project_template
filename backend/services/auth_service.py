from typing import Dict, Any, Optional
import hashlib
from dao.auth_dao import AuthDAO
from services.profile_service import ProfileService
from utils.logger_utils import setup_logger

# 配置日志
logger = setup_logger(name="auth_service")

class AuthService:
    """认证服务，提供认证相关的业务逻辑"""
    
    @staticmethod
    async def create_user(username: str, password: str, email: Optional[str] = None, 
                         phone_number: Optional[str] = None) -> Dict[str, Any]:
        """创建新用户
        
        Args:
            username: 用户名
            password: 密码（明文）
            email: 电子邮箱
            phone_number: 手机号
            
        Returns:
            Dict[str, Any]: 创建的用户信息
        """
        # 对密码进行哈希处理
        password_hash = AuthService._hash_password(password)
        user = await AuthDAO.create_user(username, password_hash, email, phone_number)
        
        # 创建用户后自动初始化一个空的用户档案
        try:
            await ProfileService.create_profile(
                user_id=user["user_id"],
                gender="other",  # 默认性别
                province=None,
                exam_year=None,
                subject_choice=None,
                score=None
            )
            logger.info(f"已为用户 {username}(ID:{user['user_id']}) 初始化空档案")
        except Exception as e:
            # 记录错误但不影响用户创建
            logger.error(f"为用户 {username}(ID:{user['user_id']}) 创建档案时出错: {str(e)}")
        
        return user
    
    @staticmethod
    async def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
        """通过用户名获取用户信息
        
        Args:
            username: 用户名
            
        Returns:
            Optional[Dict[str, Any]]: 用户信息，如果用户不存在则返回None
        """
        return await AuthDAO.get_user_by_username(username)
    
    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """通过用户ID获取用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[Dict[str, Any]]: 用户信息，如果用户不存在则返回None
        """
        user = await AuthDAO.get_user_by_id(user_id)
        if user and 'password_hash' in user:
            user.pop('password_hash', None)
        return user
    
    @staticmethod
    async def update_user(user_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """更新用户信息
        
        Args:
            user_id: 用户ID
            **kwargs: 要更新的字段，可包括email, phone_number, password
            
        Returns:
            Optional[Dict[str, Any]]: 更新后的用户信息，如果用户不存在则返回None
        """
        # 如果包含password字段，需要对密码进行哈希处理
        if 'password' in kwargs:
            kwargs['password_hash'] = AuthService._hash_password(kwargs.pop('password'))
        
        return await AuthDAO.update_user(user_id, **kwargs)
    
    @staticmethod
    async def authenticate(username: str, password: str) -> Optional[Dict[str, Any]]:
        """验证用户身份
        
        Args:
            username: 用户名
            password: 密码（明文）
            
        Returns:
            Optional[Dict[str, Any]]: 用户信息，如果认证失败则返回None
        """
        user = await AuthDAO.get_user_by_username(username)
        if not user:
            return None
        
        # 验证密码
        if AuthService._verify_password(password, user['password_hash']):
            # 返回用户信息，但不包含密码哈希
            user.pop('password_hash', None)
            return user
        
        return None
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """对密码进行哈希处理
        
        Args:
            password: 密码（明文）
            
        Returns:
            str: 密码哈希
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def _verify_password(password: str, password_hash: str) -> bool:
        """验证密码
        
        Args:
            password: 密码（明文）
            password_hash: 密码哈希
            
        Returns:
            bool: 密码是否匹配
        """
        return AuthService._hash_password(password) == password_hash 