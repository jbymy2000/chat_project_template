from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from services.topic_service import TopicService
from api.auth_api import get_current_user_id
from api.message_api import router as message_router

from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from services.message_service import MessageService
from services.profile_service import ProfileService
from api.auth_api import get_current_user_id
from utils.logger_utils import setup_logger

# 配置日志
logger = setup_logger(name="topic_api")


router = APIRouter(prefix="/api/topics", tags=["话题"])


class GraphChatRequest(BaseModel):
    message: str = Field(..., description="用户消息")

class GraphChatResponse(BaseModel):
    response: str = Field(..., description="AI响应")
    topic_id: str = Field(..., description="话题ID")
    
class MessageCreate(BaseModel):
    content: str = Field(..., description="消息内容")
    message_type: str = Field(None, description="消息类型，默认为user")

class MessageResponse(BaseModel):
    message_id: int = Field(..., description="消息ID")
    topic_id: int = Field(..., description="话题ID")
    user_id: int = Field(..., description="用户ID")
    message_type: str = Field(..., description="消息类型")
    content: str = Field(..., description="消息内容")
    created_at: str = Field(..., description="创建时间")

class TopicCreate(BaseModel):
    topic: str = Field(..., description="用户提出的问题")
    use_caption: bool = Field(True, description="是否使用文本摘要生成话题名称")

class TopicResponse(BaseModel):
    topic_id: int = Field(..., description="话题ID")
    user_id: int = Field(..., description="用户ID")
    topic: str = Field(..., description="话题名称")
    started_at: str = Field(..., description="开始时间")
    updated_at: str = Field(..., description="更新时间")

@router.post("", response_model=TopicResponse, status_code=status.HTTP_201_CREATED)
async def create_topic(
    topic_data: TopicCreate,
    current_user_id: int = Depends(get_current_user_id)
):
    """创建新话题，使用文本摘要生成话题名称"""
    try:
        # 使用Service层方法创建话题
        topic = await TopicService.create_topic_with_caption(
            current_user_id, 
            topic_data.topic, 
            topic_data.use_caption
        )
        return topic
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("", response_model=List[TopicResponse])
async def get_user_topics(
    current_user_id: int = Depends(get_current_user_id)
):
    """获取用户的所有话题"""
    topics = await TopicService.get_user_topics(current_user_id)
    return topics

@router.post("/{topic_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    topic_id: int,
    message_data: MessageCreate,
    current_user_id: int = Depends(get_current_user_id)
):
    """创建新消息"""
    try:
        # 使用提供的消息类型，如果没有提供则默认为用户消息
        message_type = message_data.message_type or "user"
        from services.message_service import MessageService
        message = await MessageService.create_message(
            topic_id, 
            current_user_id, 
            message_type, 
            message_data.content
        )
        return message
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{topic_id}/messages", response_model=List[MessageResponse])
async def get_topic_messages(
    topic_id: int,
    current_user_id: int = Depends(get_current_user_id)
):
    """获取话题的所有消息"""
    from services.message_service import MessageService
    messages = await MessageService.get_topic_messages(topic_id)
    return messages

# 包含消息子路由器，路径为/{topic_id}
router.include_router(
    message_router,
    prefix="/{topic_id}",
) 




@router.post("/{topic_id}/chat/stream")
async def chat_stream(
    topic_id: str,
    request: GraphChatRequest,
    current_user_id: int = Depends(get_current_user_id)
):
    """
    以流的形式提供对话API，实时返回AI响应
    
    Args:
        topic_id: 话题ID
        request: 包含用户消息的请求
        current_user_id: 当前用户ID
        
    Returns:
        StreamingResponse: 事件流响应
    """
    logger.info(f"用户ID {current_user_id} 请求流式聊天，话题ID: {topic_id}")
    profile = await ProfileService.get_profile(current_user_id)
    
    if not profile:
        logger.error(f"用户ID {current_user_id} 没有找到档案信息，请检查是否已创建")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="请先完善个人档案"
        )
    
    logger.info(f"用户ID {current_user_id} 的档案信息：{profile}")
    
    # 构建用户信息
    user_info = {
        "province": profile.get("province", ""),
        "score": profile.get("score", 0),
        "subjects": profile.get("subject_choice", []),
        "requirement": profile.get("requirement", "")
    }
    
    # 使用MessageService以流的方式处理消息
    return StreamingResponse(
        MessageService.stream_process_user_message(
            request.message, 
            topic_id, 
            user_info,
            current_user_id
        ),
        media_type="text/event-stream"
    ) 