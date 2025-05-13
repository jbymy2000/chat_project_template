from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from services.profile_service import ProfileService
from api.auth_api import get_current_user_id

router = APIRouter(prefix="/api/profile", tags=["用户档案"])

class ProfileCreate(BaseModel):
    gender: str = Field(default="other", description="性别")
    province: Optional[str] = Field(None, description="省份")
    exam_year: Optional[int] = Field(None, description="高考年份")
    subject_choice: Optional[List[str]] = Field(None, description="选考科目")
    score: Optional[int] = Field(None, description="高考分数")
    rank: Optional[int] = Field(None, description="等效位次")
    batch: Optional[str] = Field(None, description="批次")

class ProfileResponse(BaseModel):
    user_id: int = Field(..., description="用户ID")
    gender: str = Field(..., description="性别")
    province: Optional[str] = Field(None, description="省份")
    exam_year: Optional[int] = Field(None, description="高考年份")
    subject_choice: Optional[List[str]] = Field(None, description="选考科目")
    score: Optional[int] = Field(None, description="高考分数")
    rank: Optional[int] = Field(None, description="等效位次")
    batch: Optional[str] = Field(None, description="批次")
    requirement: Optional[str] = Field(None, description="用户需求")
    updated_at: str = Field(..., description="更新时间")

class ProfileUpdate(BaseModel):
    gender: Optional[str] = Field(None, description="性别")
    province: Optional[str] = Field(None, description="省份")
    exam_year: Optional[int] = Field(None, description="高考年份")
    subject_choice: Optional[List[str]] = Field(None, description="选考科目")
    score: Optional[int] = Field(None, description="高考分数")
    rank: Optional[int] = Field(None, description="等效位次")
    batch: Optional[str] = Field(None, description="批次")

class RequirementUpdate(BaseModel):
    requirement: str = Field(..., description="用户需求")

# 为了兼容性，保留获取当前用户档案的路由 - 移到前面避免路由冲突
@router.get("/me", response_model=ProfileResponse)
async def get_current_user_profile(current_user_id: int = Depends(get_current_user_id)):
    """获取当前用户的档案"""
    profile = await ProfileService.get_profile(current_user_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户档案不存在")
    return profile

@router.post("/{user_id}", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    user_id: int,
    profile_data: ProfileCreate,
    current_user_id: int = Depends(get_current_user_id)
):
    """创建用户档案"""
    # 检查当前用户是否有权限操作目标用户的档案
    # 此处可以添加权限检查，例如只有管理员可以操作其他用户的档案
    try:
        profile = await ProfileService.create_profile(
            user_id=user_id,
            gender=profile_data.gender,
            province=profile_data.province,
            exam_year=profile_data.exam_year,
            subject_choice=profile_data.subject_choice,
            score=profile_data.score,
            rank=profile_data.rank,
            batch=profile_data.batch
        )
        return profile
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{user_id}", response_model=ProfileResponse)
async def get_profile(
    user_id: int,
    current_user_id: int = Depends(get_current_user_id)
):
    """获取指定用户的档案"""
    # 检查当前用户是否有权限查看目标用户的档案
    profile = await ProfileService.get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户档案不存在")
    return profile

@router.put("/{user_id}", response_model=ProfileResponse)
async def update_profile(
    user_id: int,
    profile_data: ProfileUpdate,
    current_user_id: int = Depends(get_current_user_id)
):
    """更新用户档案"""
    # 检查当前用户是否有权限更新目标用户的档案
    
    # 构建更新参数
    update_data = {}
    for field, value in profile_data.dict(exclude_unset=True).items():
        if value is not None:
            update_data[field] = value
    
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="没有提供有效的更新字段")
    
    try:
        updated_profile = await ProfileService.update_profile(user_id, **update_data)
        if not updated_profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户档案不存在")
        return updated_profile
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/{user_id}/requirement", response_model=ProfileResponse)
async def update_requirement(
    user_id: int,
    requirement_data: RequirementUpdate,
    current_user_id: int = Depends(get_current_user_id)
):
    """更新用户需求"""
    # 检查当前用户是否有权限更新目标用户的需求
    
    try:
        updated_profile = await ProfileService.update_requirement(
            user_id, 
            requirement_data.requirement
        )
        if not updated_profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户档案不存在")
        return updated_profile
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) 