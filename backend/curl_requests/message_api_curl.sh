#!/bin/bash

# 消息API的curl请求

# 设置token变量 - 需要先通过auth_api_curl.sh获取token
TOKEN="YOUR_TOKEN_HERE"

# 普通聊天请求
curl -X POST "http://localhost:8000/api/topic/1/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "message": "我的数学成绩是120分，想报考计算机专业，请给我一些建议"
  }'

# 流式聊天请求
curl -X POST "http://localhost:8000/api/topic/1/chat/stream" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -H "Authorization: Bearer $TOKEN" \
  -N \
  -d '{
    "message": "我的数学成绩是120分，想报考计算机专业，请给我一些建议"
  }'
# 注意：
# 1. 请将上述URL中的"1"替换为实际的话题ID
# 2. 该API需要用户已创建个人档案，否则会返回错误 