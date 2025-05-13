from fastapi import APIRouter
from utils.logger_utils import setup_logger

# 配置日志
logger = setup_logger(name="message_api")

router = APIRouter(prefix="/api/message", tags=["消息"])