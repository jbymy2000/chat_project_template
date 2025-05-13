#!/bin/bash

# 认证API的curl请求

# 1. 用户注册
echo "===== 注册新用户 ====="
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123",
    "email": "test@example.com",
    "phone_number": "13800138000"
  }'

echo -e "\n"

# 2. 用户登录获取token
echo "===== 用户登录获取token ====="
curl -X POST "http://localhost:8000/api/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser1&password=password123"

echo -e "\n"

# 说明：
# 请在使用其他API前先登录获取token
# 获取token后，在后续请求中设置Authorization头：
# -H "Authorization: Bearer {YOUR_TOKEN_HERE}" 