"""
话题API的单元测试
"""
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import status
from datetime import datetime
import os
import sys

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.topic_api import router
from services.topic_service import TopicService
from services.message_service import MessageService

# 创建测试客户端
@pytest.fixture
def client():
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)

# 模拟用户ID (current_user_id)
@pytest.fixture
def mock_current_user_id():
    return 1

# 模拟话题数据
@pytest.fixture
def mock_topic_data():
    return {
        "topic": "测试话题"
    }

# 模拟创建的话题
@pytest.fixture
def mock_created_topic():
    return {
        "topic_id": 1,
        "user_id": 1,
        "topic": "测试话题",
        "started_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

# 模拟消息数据
@pytest.fixture
def mock_message_data():
    return {
        "content": "测试消息"
    }

# 模拟创建的消息
@pytest.fixture
def mock_created_message():
    return {
        "message_id": 1,
        "topic_id": 1,
        "user_id": 1,
        "message_type": "user",
        "content": "测试消息",
        "created_at": datetime.now().isoformat()
    }

# 模拟get_current_user_id依赖
@pytest.fixture
def mock_get_current_user_id(mock_current_user_id):
    with patch("api.topic_api.get_current_user_id") as mock:
        mock.return_value = mock_current_user_id
        yield mock

# 测试创建话题
@pytest.mark.asyncio
async def test_create_topic(client, mock_get_current_user_id, mock_topic_data, mock_created_topic):
    # 模拟 TopicService.create_topic
    with patch.object(TopicService, "create_topic", new_callable=AsyncMock) as mock_create_topic:
        mock_create_topic.return_value = mock_created_topic
        
        # 发送创建话题请求
        response = client.post("/api/topics", json=mock_topic_data)
        
        # 验证响应
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["topic_id"] == mock_created_topic["topic_id"]
        assert data["topic"] == mock_created_topic["topic"]
        
        # 验证调用服务
        mock_create_topic.assert_called_once_with(1, mock_topic_data["topic"])

# 测试创建话题错误处理
@pytest.mark.asyncio
async def test_create_topic_error(client, mock_get_current_user_id, mock_topic_data):
    # 模拟 TopicService.create_topic 抛出异常
    with patch.object(TopicService, "create_topic", new_callable=AsyncMock) as mock_create_topic:
        mock_create_topic.side_effect = ValueError("创建话题失败")
        
        # 发送创建话题请求
        response = client.post("/api/topics", json=mock_topic_data)
        
        # 验证响应
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "创建话题失败"

# 测试获取用户话题
@pytest.mark.asyncio
async def test_get_user_topics(client, mock_get_current_user_id, mock_created_topic):
    # 模拟 TopicService.get_user_topics
    with patch.object(TopicService, "get_user_topics", new_callable=AsyncMock) as mock_get_user_topics:
        mock_get_user_topics.return_value = [mock_created_topic]
        
        # 发送获取用户话题请求
        response = client.get("/api/topics")
        
        # 验证响应
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["topic_id"] == mock_created_topic["topic_id"]
        assert data[0]["topic"] == mock_created_topic["topic"]
        
        # 验证调用服务
        mock_get_user_topics.assert_called_once_with(1)

# 测试创建消息
@pytest.mark.asyncio
async def test_create_message(client, mock_get_current_user_id, mock_message_data, mock_created_message):
    # 模拟 MessageService.create_message
    with patch.object(MessageService, "create_message", new_callable=AsyncMock) as mock_create_message:
        mock_create_message.return_value = mock_created_message
        
        # 发送创建消息请求
        response = client.post("/api/topics/1/messages", json=mock_message_data)
        
        # 验证响应
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["message_id"] == mock_created_message["message_id"]
        assert data["content"] == mock_created_message["content"]
        
        # 验证调用服务
        mock_create_message.assert_called_once_with(1, 1, "user", mock_message_data["content"])

# 测试创建消息错误处理
@pytest.mark.asyncio
async def test_create_message_error(client, mock_get_current_user_id, mock_message_data):
    # 模拟 MessageService.create_message 抛出异常
    with patch.object(MessageService, "create_message", new_callable=AsyncMock) as mock_create_message:
        mock_create_message.side_effect = ValueError("话题不存在")
        
        # 发送创建消息请求
        response = client.post("/api/topics/1/messages", json=mock_message_data)
        
        # 验证响应
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "话题不存在"

# 测试获取话题消息
@pytest.mark.asyncio
async def test_get_topic_messages(client, mock_get_current_user_id, mock_created_message):
    # 模拟 MessageService.get_topic_messages
    with patch.object(MessageService, "get_topic_messages", new_callable=AsyncMock) as mock_get_topic_messages:
        mock_get_topic_messages.return_value = [mock_created_message]
        
        # 发送获取话题消息请求
        response = client.get("/api/topics/1/messages")
        
        # 验证响应
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["message_id"] == mock_created_message["message_id"]
        assert data[0]["content"] == mock_created_message["content"]
        
        # 验证调用服务
        mock_get_topic_messages.assert_called_once_with(1) 