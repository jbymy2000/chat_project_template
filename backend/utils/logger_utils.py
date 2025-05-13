import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name="qihang_ai", log_file="logs/qihang_ai.log", level=logging.INFO):
    """
    设置并返回一个配置好的日志记录器
    
    参数:
        name: 日志记录器名称
        log_file: 日志文件路径
        level: 日志级别
    
    返回:
        配置好的日志记录器
    """
    # 创建日志目录
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # 配置日志
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 如果已经有处理器，不重复添加
    if logger.handlers:
        return logger
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # 创建文件处理器
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(level)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # 添加处理器到日志记录器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger 