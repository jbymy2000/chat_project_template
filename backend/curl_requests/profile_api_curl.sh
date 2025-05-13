#!/bin/bash

# 用户档案API的curl请求

# 设置token变量 - 需要先通过auth_api_curl.sh获取token
TOKEN="YOUR_TOKEN_HERE"
USER_ID=1  # 设置要操作的用户ID

# 1. 创建用户档案
echo "===== 创建用户档案 ====="
curl -X POST "http://localhost:8000/api/profile/${USER_ID}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "gender": "male",
    "province": "广东",
    "exam_year": 2024,
    "subject_choice": ["物理", "化学"],
    "score": 650
  }'

echo -e "\n"

# 2. 获取用户档案
echo "===== 获取用户档案 ====="
curl -X GET "http://localhost:8000/api/profile/${USER_ID}" \
  -H "Authorization: Bearer $TOKEN"

echo -e "\n"

# 3. 获取当前登录用户的档案
echo "===== 获取当前用户档案 ====="
curl -X GET "http://localhost:8000/api/profile/me" \
  -H "Authorization: Bearer $TOKEN"

echo -e "\n"

# 4. 更新用户档案
echo "===== 更新用户档案 ====="
curl -X PUT "http://localhost:8000/api/profile/${USER_ID}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "province": "浙江",
    "score": 680
  }'

echo -e "\n"

# 5. 更新用户需求
echo "===== 更新用户需求 ====="
curl -X PUT "http://localhost:8000/api/profile/${USER_ID}/requirement" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "requirement": "想要报考理工类专业，希望未来有好的就业前景"
  }'

echo -e "\n" 