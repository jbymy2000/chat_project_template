import clickhouse_connect
import json
from typing import Dict, List, Any, Optional
import logging
from utils.config_utils import get_clickhouse_config

# 配置日志
logger = logging.getLogger("clickhouse_db")

class ClickHouseDB:
    _client = None

    @classmethod
    def get_client(cls):
        """获取ClickHouse客户端连接"""
        if cls._client is None:
            config = get_clickhouse_config()
            try:
                cls._client = clickhouse_connect.get_client(
                    host=config.get('host', 'localhost'),
                    port=config.get('port', 8123),  # HTTP接口端口
                    username=config.get('username', 'default'),
                    password=config.get('password', ''),
                    database=config.get('database', 'default')
                )
                logger.info("成功创建ClickHouse客户端连接")
            except Exception as e:
                logger.error(f"无法创建ClickHouse客户端连接: {str(e)}")
                raise Exception(f"无法创建ClickHouse客户端连接: {str(e)}")
        return cls._client

    @classmethod
    def close_client(cls):
        """关闭ClickHouse客户端连接"""
        if cls._client:
            # clickhouse_connect客户端支持显式关闭
            cls._client.close()
            cls._client = None
            logger.info("ClickHouse客户端连接已关闭")

    @classmethod
    def execute(cls, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """执行ClickHouse查询并返回结果"""
        client = cls.get_client()
        try:
            # 使用clickhouse_connect的查询方法
            query_result = client.query(query, parameters=params or {})
            # 获取结果的行和列名
            rows = query_result.result_rows
            column_names = query_result.column_names
            
            # 将结果转换为字典列表
            result_dicts = []
            for row in rows:
                row_dict = {}
                for i, value in enumerate(row):
                    row_dict[column_names[i]] = value
                result_dicts.append(row_dict)
            
            return result_dicts
        except Exception as e:
            logger.error(f"执行ClickHouse查询失败: {str(e)}, 查询: {query}")
            raise Exception(f"执行查询失败: {str(e)}") 