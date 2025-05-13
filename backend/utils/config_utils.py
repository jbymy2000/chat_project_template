import os
import yaml
from dotenv import load_dotenv
from utils.logger_utils import setup_logger
from typing import Dict, Any

# 配置日志
logger = setup_logger(name="config", log_file="logs/config.log")

# 加载环境变量
load_dotenv()

class ConfigManager:
    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._config is None:
            self.load_config()

    def load_config(self):
        """
        加载配置文件
        
        返回:
            配置字典
        """
        config_path = os.environ.get("CONFIG_PATH", "config.yml")
        
        try:
            logger.info(f"正在加载配置文件: {config_path}")
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
            
            # 检查必要的配置项
            if 'jwt' not in self._config:
                logger.warning("配置文件中缺少JWT配置，将使用默认值")
                self._config['jwt'] = {
                    'secret_key': os.environ.get("JWT_SECRET_KEY", "your-secret-key-for-jwt-token-generation"),
                    'algorithm': "HS256",
                    'access_token_expire_minutes': 30
                }
            
            if 'postgresql' not in self._config:
                logger.warning("配置文件中缺少PostgreSQL配置，将使用默认值")
                self._config['postgresql'] = {
                    'host': 'localhost',
                    'port': 5432,
                    'user': 'postgres',
                    'password': '',
                    'database': 'postgres'
                }
            
            if 'clickhouse' not in self._config:
                logger.warning("配置文件中缺少ClickHouse配置，将使用默认值")
                self._config['clickhouse'] = {
                    'host': 'localhost',
                    'port': 9000,
                    'username': 'default',
                    'password': '',
                    'database': 'default'
                }
            
            logger.info("配置文件加载成功")
            return self._config
        
        except Exception as e:
            logger.error(f"加载配置文件时发生错误: {str(e)}")
            # 返回默认配置
            self._config = {
                'jwt': {
                    'secret_key': os.environ.get("JWT_SECRET_KEY", "your-secret-key-for-jwt-token-generation"),
                    'algorithm': "HS256",
                    'access_token_expire_minutes': 30
                },
                'postgresql': {
                    'host': 'localhost',
                    'port': 5432,
                    'user': 'postgres',
                    'password': '',
                    'database': 'postgres'
                },
                'clickhouse': {
                    'host': 'localhost',
                    'port': 9000,
                    'user': 'default',
                    'password': '',
                    'database': 'default'
                }
            }
            return self._config

    def get_jwt_config(self) -> Dict[str, Any]:
        """获取JWT配置"""
        return self._config.get('jwt', {})

    def get_postgresql_config(self) -> Dict[str, Any]:
        """获取PostgreSQL配置"""
        return self._config.get('postgresql', {})

    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self._config.get('logging', {})
        
    def get_clickhouse_config(self) -> Dict[str, Any]:
        """获取ClickHouse配置"""
        return self._config.get('clickhouse', {})

# 创建全局配置管理器实例
config_manager = ConfigManager()

def get_jwt_config() -> Dict[str, Any]:
    """获取JWT配置的便捷函数"""
    return config_manager.get_jwt_config()

def get_postgresql_config() -> Dict[str, Any]:
    """获取PostgreSQL配置的便捷函数"""
    return config_manager.get_postgresql_config()

def get_logging_config() -> Dict[str, Any]:
    """获取日志配置的便捷函数"""
    return config_manager.get_logging_config() 

def get_clickhouse_config() -> Dict[str, Any]:
    """获取ClickHouse配置的便捷函数"""
    return config_manager.get_clickhouse_config() 