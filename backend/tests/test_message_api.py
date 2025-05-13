"""
消息API的单元测试
"""
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import status
import os
import sys

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.message_api import router
from services.message_service import MessageService
from services.profile_service import ProfileService

# 创建测试客户端 - 注意：需要在路径中包括topic_id参数
@pytest.fixture
def client():
    from fastapi import FastAPI, APIRouter
    # 创建一个父路由器，以模拟topic_api中的路由设置
    parent_router = APIRouter(prefix="/api/topics")
    parent_router.include_router(router, prefix="/{topic_id}")
    
    app = FastAPI()
    app.include_router(parent_router)
    return TestClient(app)

# 模拟用户ID (current_user_id)
@pytest.fixture
def mock_current_user_id():
    return 1

# 模拟图谱聊天请求数据
@pytest.fixture
def mock_graph_chat_request():
    return {
        "message": "这是一个测试消息"
    }

# 模拟用户档案
@pytest.fixture
def mock_profile():
    return {
        "user_id": 1,
        "name": "测试用户",
        "province": "北京",
        "score": 650,
        "subject_choice": ["数学", "物理", "化学"],
        "requirement": "希望进入一流大学"
    }

# 模拟图谱聊天响应
@pytest.fixture
def mock_graph_chat_response():
    return "这是AI的回复内容"

# 模拟get_current_user_id依赖
@pytest.fixture
def mock_get_current_user_id(mock_current_user_id):
    with patch("api.message_api.get_current_user_id") as mock:
        mock.return_value = mock_current_user_id
        yield mock

# 测试没有用户档案时的错误处理
@pytest.mark.asyncio
async def test_chat_with_graph_no_profile(client, mock_get_current_user_id, mock_graph_chat_request):
    # 模拟 ProfileService.get_profile 返回 None
    with patch.object(ProfileService, "get_profile", new_callable=AsyncMock) as mock_get_profile:
        mock_get_profile.return_value = None
        
        # 发送图谱聊天请求
        response = client.post("/api/topics/123/graph", json=mock_graph_chat_request)
        
        # 验证响应
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "请先完善个人档案"
        
        # 验证调用服务
        mock_get_profile.assert_called_once_with(1)

