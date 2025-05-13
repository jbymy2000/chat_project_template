from fastapi import APIRouter, File, UploadFile, HTTPException, Request
import requests
import json
import base64
import io
import os
from typing import Optional
from pydantic import BaseModel
import logging

# 创建路由器
router = APIRouter(prefix="/api/speech", tags=["语音识别"])

# 日志配置
logger = logging.getLogger("qihang_ai")

# 百度语音识别API配置
API_KEY = "zopm8aWv6zviqfMtubzLkbDN"
SECRET_KEY = "qIGXFJQzWa0MBhlTEVfm1YawwNNcdO2T"

class SpeechResponse(BaseModel):
    text: str
    success: bool
    error_msg: Optional[str] = None

def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    response = requests.post(url, params=params)
    result = response.json()
    access_token = result.get("access_token")
    if not access_token:
        logger.error(f"获取百度语音识别Token失败: {result}")
        raise HTTPException(status_code=500, detail="获取语音识别服务授权失败")
    return access_token

@router.post("/recognize", response_model=SpeechResponse, summary="语音识别", description="将语音转换为文本")
async def recognize_speech(file: UploadFile = File(...)):
    """
    接收语音文件并使用百度语音识别API转换为文本
    """
    try:
        # 读取上传的文件内容
        audio_content = await file.read()
        
        # 检查文件大小不超过限制
        if len(audio_content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="文件大小超过限制")
        
        # 记录音频内容信息
        logger.info(f"收到音频文件: {file.filename}, 大小: {len(audio_content)} bytes, 格式: {file.content_type}")
            
        # Base64编码音频数据
        audio_base64 = base64.b64encode(audio_content).decode('utf-8')
        
        # 获取访问令牌
        access_token = get_access_token()
        
        # 调用百度语音识别API
        url = "https://vop.baidu.com/pro_api"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # 确定音频格式
        # 根据文件类型确定音频格式 - 默认pcm, webm用aac, wav用wav
        audio_format = "pcm"
        if file.content_type:
            if "webm" in file.content_type:
                audio_format = "m4a" # 对于webm录音, 通常使用aac或m4a格式
            elif "wav" in file.content_type:
                audio_format = "wav"
        
        # 准备请求数据
        payload = {
            "format": audio_format,  # 音频格式，根据实际情况调整
            "rate": 16000,    # 采样率
            "channel": 1,     # 声道数
            "cuid": "WmOp9G3N4oIswYLyLqaxm4xKqL10B3D2",
            "token": access_token,
            "dev_pid": 80001, # 普通话
            "speech": audio_base64,
            "len": len(audio_content)
        }
        
        logger.info(f"发送语音识别请求，格式: {audio_format}, 大小: {len(audio_content)} bytes")
        
        # 发送请求
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()
        
        logger.info(f"百度语音识别响应: {result}")
        
        # 检查响应
        if result.get("err_no") == 0 and "result" in result:
            recognized_text = result["result"][0]
            logger.info(f"语音识别成功: {recognized_text}")
            return SpeechResponse(text=recognized_text, success=True)
        else:
            error_msg = result.get("err_msg", "未知错误")
            logger.error(f"语音识别失败: {error_msg}")
            return SpeechResponse(text="", success=False, error_msg=error_msg)
            
    except Exception as e:
        logger.exception("语音识别过程中发生错误")
        return SpeechResponse(text="", success=False, error_msg=str(e))

@router.post("/recognize-blob", response_model=SpeechResponse, summary="Blob语音识别", description="将Blob数据转换为文本")
async def recognize_speech_blob(request: Request, file: UploadFile = File(...)):
    """
    接收Blob格式的语音数据并使用百度语音识别API转换为文本
    特别适用于前端直接发送录音的Blob数据
    """
    # 记录请求信息以便调试
    client_host = request.client.host if request.client else "Unknown"
    logger.info(f"接收到来自 {client_host} 的Blob语音识别请求，文件: {file.filename}, 类型: {file.content_type}")
    
    # 处理与recognize_speech相同
    return await recognize_speech(file) 