#!/bin/bash

# 专家数据API的curl请求

# 设置token变量 - 需要先通过auth_api_curl.sh获取token
TOKEN="YOUR_TOKEN_HERE"

# 1. 获取专家列表（基本查询）
echo "===== 获取专家列表 ====="
curl -v -X GET "http://localhost:8000/api/data/specialist?page=1&page_size=10" \
  -H "Authorization: Bearer $TOKEN"

echo -e "\n"

# 2. 获取专家列表（带筛选条件）
echo "===== 获取专家列表（带筛选条件） ====="
curl -v -X GET "http://localhost:8000/api/data/specialist?page=1&page_size=10&filters=%7B%22name%22%3A%22张三%22%7D" \
  -H "Authorization: Bearer $TOKEN"

echo -e "\n"
# 注意：filters=%7B%22name%22%3A%22张三%22%7D 是 {"name":"张三"} 的URL编码

# 3. 获取专家列表（按省份筛选）
echo "===== 获取专家列表（按省份筛选） ====="
curl -v -X GET "http://localhost:8000/api/data/specialist?page=1&page_size=10&province_name=北京" \
  -H "Authorization: Bearer $TOKEN"

echo -e "\n"

# 4. 获取专家列表（带排序）
echo "===== 获取专家列表（按生日降序排序） ====="
curl -v -X GET "http://localhost:8000/api/data/specialist?page=1&page_size=10&sort_by=birthday&sort_order=DESC" \
  -H "Authorization: Bearer $TOKEN"

echo -e "\n"

# 5. 获取专家列表（带筛选和排序）
echo "===== 获取专家列表（带筛选和排序） ====="
curl -v -X GET "http://localhost:8000/api/data/specialist?page=1&page_size=15&filters=%7B%22education%22%3A%22博士%22%7D&sort_by=age&sort_order=ASC" \
  -H "Authorization: Bearer $TOKEN"

echo -e "\n"

# 6. 获取专家列表（综合筛选）
echo "===== 获取专家列表（多条件综合筛选） ====="
curl -v -X GET "http://localhost:8000/api/data/specialist?page=1&page_size=15&filters=%7B%22education%22%3A%22博士%22%7D&province_name=上海&sort_by=age&sort_order=ASC" \
  -H "Authorization: Bearer $TOKEN"

echo -e "\n"

# 7. 通过ID获取专家详情（假设路由格式，需要根据实际情况调整）
echo "===== 通过ID获取专家详情 ====="
curl -v -X GET "http://localhost:8000/api/data/specialist/id/YOUR_SPECIALIST_ID_HERE" \
  -H "Authorization: Bearer $TOKEN"

echo -e "\n"

# 8. 通过指定字段获取专家详情（假设路由格式，需要根据实际情况调整）
echo "===== 通过姓名获取专家详情 ====="
curl -v -X GET "http://localhost:8000/api/data/specialist/field/name/张三" \
  -H "Authorization: Bearer $TOKEN"

echo -e "\n"

# 9. 访问JSON嵌套字段排序的例子
echo "===== 获取专家列表（按JSON嵌套字段排序） ====="
curl -v -X GET "http://localhost:8000/api/data/specialist?page=1&page_size=10&sort_by=info.education&sort_order=DESC" \
  -H "Authorization: Bearer $TOKEN"

echo -e "\n"

# 一些可能用到的URL编码筛选条件示例：
# {"name":"张三"} -> %7B%22name%22%3A%22张三%22%7D
# {"age":30} -> %7B%22age%22%3A30%7D
# {"education":"博士"} -> %7B%22education%22%3A%22博士%22%7D
# {"specialty":"计算机"} -> %7B%22specialty%22%3A%22计算机%22%7D

# 注意: 执行这些请求之前，请先替换TOKEN和实际的专家ID或字段值 