from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from datetime import datetime
from contextlib import asynccontextmanager

from utils.logger_utils import setup_logger
from utils.config_utils import get_jwt_config, get_postgresql_config, get_logging_config, get_clickhouse_config
from dao import Database
from api.auth_api import router as auth_router
from api.topic_api import router as topic_router
from api.profile_api import router as profile_router
from api.specialist_api import router as specialist_router
from api.speech_api import router as speech_router

# 获取配置
jwt_config = get_jwt_config()
postgresql_config = get_postgresql_config()
logging_config = get_logging_config()
clickhouse_config = get_clickhouse_config()

# 创建目录
os.makedirs("logs", exist_ok=True)
os.makedirs("static", exist_ok=True)

# 配置日志
logger = setup_logger(name="qihang_ai")

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # 启动时执行
#     logger.info("XXAI服务启动")
#     await Database.get_pool()
#     yield
#     # 关闭时执行
#     logger.info("XXAI服务关闭")
#     await Database.close_pool()

# 创建FastAPI应用
app = FastAPI(
    title="XXAI服务",
    description="XXAI后端服务API",
    version="1.0.0",
    # lifespan=lifespan
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://localhost:8000"],  # 允许的前端域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# 包含路由模块
app.include_router(auth_router)
app.include_router(topic_router)
app.include_router(profile_router)
app.include_router(specialist_router)
app.include_router(speech_router)

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/health", summary="健康检查接口", description="用于检查服务是否正常运行")
async def health_check():
    """健康检查接口，返回服务状态和当前时间"""
    logger.info("健康检查接口被调用")
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "XXAI服务"
    }

if __name__ == "__main__":
    logger.info("正在启动XXAI服务...")
    import asyncio
    import signal
    
    def handle_exit(signum, frame):
        logger.info("接收到终止信号，正在关闭服务...")
        raise KeyboardInterrupt()
    
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    
    uvicorn.run("qihang_ai:app", host="0.0.0.0", port=8000, reload=False)
