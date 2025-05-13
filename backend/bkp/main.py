from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import yaml
from langchain_core.messages import HumanMessage, SystemMessage
from lib.deepseek_chatopenai import DeepseekChatOpenAI
from langchain_community.chat_message_histories import PostgresChatMessageHistory

# 获取当前文件所在目录的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 构建.env文件的完整路径
ENV_PATH = os.path.join(BASE_DIR, '.env')

# 加载环境变量
if not load_dotenv(ENV_PATH):
    print(f"警告: 未找到.env文件: {ENV_PATH}")
    print("请确保.env文件存在并包含必要的环境变量")

# 验证必要的环境变量
required_env_vars = ['OPENAI_API_KEY', 'OPENAI_API_BASE']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise EnvironmentError(f"缺少必要的环境变量: {', '.join(missing_vars)}")

# 加载配置文件
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

# 初始化FastAPI应用
app = FastAPI(title="AI Chat API")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置OpenAI
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_BASE"] = os.getenv("OPENAI_API_BASE")

# 初始化DeepseekChatOpenAI模型
llm = DeepseekChatOpenAI(
    model="deepseek-r1-250120",
    streaming=True
)

# 创建logs目录（如果不存在）
if not os.path.exists('logs'):
    os.makedirs('logs')

class ChatRequest(BaseModel):
    query: str
    conversation_id: str | None = None

async def generate_response(request: ChatRequest):
    # 生成日志文件名（使用当前时间）
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f'logs/server_chat_{timestamp}.txt'
    
    try:
        # 初始化数据库连接
        db_config = config['postgresql']
        connection_string = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        
        # 初始化聊天历史记录
        history = PostgresChatMessageHistory(
            connection_string=connection_string,
            session_id=request.conversation_id or "default_session"
        )
        
        messages = [
            SystemMessage(content="你是个乐于助人的助手"),
            HumanMessage(content=request.query)
        ]
        
        # 打开日志文件
        with open(log_file, 'w', encoding='utf-8') as f:
            # 记录请求信息
            f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Query: {request.query}\n")
            f.write(f"Conversation ID: {request.conversation_id}\n")
            f.write("-" * 50 + "\n")
            
            # 流式返回响应
            async for chunk in llm._astream(messages):
                if chunk.message.content:
                    # 构造JSON响应
                    response_data = {
                        "content": chunk.message.content,
                        "content_type": "answer"
                    }
                    # 记录到日志文件
                    f.write(f"Answer: {chunk.message.content}\n")
                    yield f"data: {json.dumps(response_data, ensure_ascii=False)}\n\n"
                
                # 如果有推理内容，也返回
                if "reasoning" in chunk.message.additional_kwargs:
                    reasoning_data = {
                        "content": chunk.message.additional_kwargs["reasoning"],
                        "content_type": "reasoning"
                    }
                    # 记录到日志文件
                    f.write(f"Reasoning: {chunk.message.additional_kwargs['reasoning']}\n")
                    yield f"data: {json.dumps(reasoning_data, ensure_ascii=False)}\n\n"
                
                # 确保日志立即写入文件
                f.flush()
            
            # 保存对话历史
            history.add_user_message(request.query)
            history.add_ai_message(chunk.message.content)

    except Exception as e:
        error_data = {
            "content": str(e),
            "content_type": "error"
        }
        # 记录错误到日志文件
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"Error: {str(e)}\n")
        yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    return StreamingResponse(
        generate_response(request),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 