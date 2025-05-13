#!/bin/bash

# 话题API的curl请求

# 设置token变量 - 需要先通过auth_api_curl.sh获取token
TOKEN="YOUR_TOKEN_HERE"

# 1. 创建新话题
echo "===== 创建新话题 ====="
curl -X POST "http://localhost:8000/api/topics" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "topic": "高考志愿填报"
  }'

echo -e "\n"

# 2. 获取用户的所有话题
echo "===== 获取用户话题列表 ====="
curl -X GET "http://localhost:8000/api/topics" \
  -H "Authorization: Bearer $TOKEN"

echo -e "\n"

# 3. 在话题中创建新消息
echo "===== 在话题中创建新消息 ====="
curl -X POST "http://localhost:8000/api/topics/1/messages" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "content": "我想了解下计算机专业的就业前景"
  }'

echo -e "\n"

# 4. 获取话题中的所有消息
echo "===== 获取话题中的所有消息 ====="
curl -X GET "http://localhost:8000/api/topics/1/messages" \
  -H "Authorization: Bearer $TOKEN"

echo -e "\n"

# 注意：请将上述URL中的"1"替换为实际的话题ID 