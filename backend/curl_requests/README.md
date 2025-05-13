# API 接口 curl 请求使用说明

本目录包含了系统各 API 接口的 curl 请求示例，方便开发和测试。

## 文件说明

1. `auth_api_curl.sh` - 认证 API 请求，包括注册和登录
2. `topic_api_curl.sh` - 话题相关 API 请求
3. `message_api_curl.sh` - 消息相关 API 请求
4. `profile_api_curl.sh` - 用户档案相关 API 请求
5. `specialist_api_curl.sh` - 专家数据相关 API 请求

## 使用方法

### 1. 添加执行权限

```bash
chmod +x curl_requests/*.sh
```

### 2. 按顺序执行

首先执行认证 API 获取 token：

```bash
./curl_requests/auth_api_curl.sh
```

获取 token 后，修改其他脚本中的`TOKEN`变量：

```bash
# 编辑脚本
vim curl_requests/topic_api_curl.sh
vim curl_requests/message_api_curl.sh
vim curl_requests/profile_api_curl.sh
vim curl_requests/specialist_api_curl.sh

# 修改TOKEN变量
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxx..."
```

然后执行其他 API 请求：

```bash
./curl_requests/topic_api_curl.sh
./curl_requests/message_api_curl.sh
./curl_requests/profile_api_curl.sh
./curl_requests/specialist_api_curl.sh
```

## 注意事项

1. 请确保系统服务已经启动并在`http://localhost:8000`运行
2. 执行前请修改脚本中的请求参数以适应实际情况
3. 话题 ID 和用户 ID 等需要根据实际情况进行替换
4. 使用消息 API 前，请确保已经创建用户档案
5. 使用专家数据 API 时，注意替换筛选条件和记录键

## 专家数据 API 参数说明

专家数据 API 支持以下查询参数：

-   `page`: 页码，从 1 开始
-   `page_size`: 每页数据条数，1-100
-   `filters`: JSON 格式筛选条件，需 URL 编码，例如：`{"name":"张三"}`
-   `sort_by`: 排序字段，支持嵌套 JSON 字段，使用点分隔，例如：`info.education`
-   `sort_order`: 排序方向，`ASC`升序或`DESC`降序
