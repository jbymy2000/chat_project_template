"""
pytest配置文件，设置通用的fixture和测试环境
"""
import pytest
import os
import sys
from unittest.mock import patch, AsyncMock

# 确保可以导入项目模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 模拟数据库连接池
@pytest.fixture(autouse=True)
def mock_db_pool():
    """
    自动模拟数据库连接池，避免在测试中实际连接数据库
    """
    with patch("dao.database.Database.get_pool", new_callable=AsyncMock) as mock:
        mock.return_value = AsyncMock()
        yield mock 