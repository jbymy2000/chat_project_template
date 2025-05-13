"""
认证API的单元测试
"""
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import status
import jwt
from datetime import datetime, timedelta
import os
import sys

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.auth_api import router, create_access_token, SECRET_KEY, ALGORITHM
from services.auth_service import AuthService

# 创建测试客户端
@pytest.fixture
def client():
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)

# 模拟用户数据
@pytest.fixture
def mock_user_data():
    return {
        "username": "testuser",
        "password": "password123",
        "email": "test@example.com",
        "phone_number": "13800138000"
    }

# 模拟创建的用户
@pytest.fixture
def mock_created_user():
    return {
        "user_id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "phone_number": "13800138000",
        "created_at": datetime.now().isoformat()
    }

# 测试用户注册
@pytest.mark.asyncio
async def test_register(client, mock_user_data, mock_created_user):
    # 模拟 AuthService.create_user
    with patch.object(AuthService, "create_user", new_callable=AsyncMock) as mock_create_user:
        mock_create_user.return_value = mock_created_user
        
        # 发送注册请求
        response = client.post("/api/auth/register", json=mock_user_data)
        
        # 验证响应
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == mock_created_user["username"]
        assert data["email"] == mock_created_user["email"]
        
        # 验证调用服务
        mock_create_user.assert_called_once_with(
            username=mock_user_data["username"],
            password=mock_user_data["password"],
            email=mock_user_data["email"],
            phone_number=mock_user_data["phone_number"]
        )

# 测试用户注册错误处理
@pytest.mark.asyncio
async def test_register_error(client, mock_user_data):
    # 模拟 AuthService.create_user 抛出异常
    with patch.object(AuthService, "create_user", new_callable=AsyncMock) as mock_create_user:
        mock_create_user.side_effect = ValueError("用户名已存在")
        
        # 发送注册请求
        response = client.post("/api/auth/register", json=mock_user_data)
        
        # 验证响应
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "用户名已存在"

# 测试登录
@pytest.mark.asyncio
async def test_login(client, mock_created_user):
    # 模拟 AuthService.authenticate
    with patch.object(AuthService, "authenticate", new_callable=AsyncMock) as mock_authenticate:
        mock_authenticate.return_value = mock_created_user
        
        # 发送登录请求
        form_data = {
            "username": "testuser",
            "password": "password123"
        }
        response = client.post("/api/auth/token", data=form_data)
        
        # 验证响应
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        
        # 验证令牌
        token = data["access_token"]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == mock_created_user["username"]
        assert payload["user_id"] == mock_created_user["user_id"]
        assert payload["role"] == "user"
        
        # 验证调用服务
        mock_authenticate.assert_called_once_with("testuser", "password123")

# 测试登录失败
@pytest.mark.asyncio
async def test_login_failed(client):
    # 模拟 AuthService.authenticate 返回 None（认证失败）
    with patch.object(AuthService, "authenticate", new_callable=AsyncMock) as mock_authenticate:
        mock_authenticate.return_value = None
        
        # 发送登录请求
        form_data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        response = client.post("/api/auth/token", data=form_data)
        
        # 验证响应
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "用户名或密码错误"

# 测试创建访问令牌
def test_create_access_token():
    # 准备数据
    data = {"user_id": 1, "sub": "testuser", "role": "user"}
    expires_delta = timedelta(minutes=30)
    
    # 创建令牌
    token = create_access_token(data, expires_delta)
    
    # 验证令牌
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["user_id"] == data["user_id"]
    assert payload["sub"] == data["sub"]
    assert payload["role"] == data["role"]
    assert "exp" in payload 