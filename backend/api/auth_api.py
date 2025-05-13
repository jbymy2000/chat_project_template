from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, EmailStr
import jwt
from datetime import datetime, timedelta

from services.auth_service import AuthService
from utils.config_utils import get_jwt_config

router = APIRouter(prefix="/api/auth", tags=["认证"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")
jwt_config = get_jwt_config()
SECRET_KEY = jwt_config.get("secret_key")
ALGORITHM = jwt_config.get("algorithm")
ACCESS_TOKEN_EXPIRE_MINUTES = jwt_config.get("access_token_expire_minutes")

class UserCreate(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    email: Optional[EmailStr] = Field(None, description="电子邮箱")
    phone_number: Optional[str] = Field(None, description="手机号")

class UserResponse(BaseModel):
    user_id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: Optional[str] = Field(None, description="电子邮箱")
    phone_number: Optional[str] = Field(None, description="手机号")
    created_at: str = Field(..., description="创建时间")

class Token(BaseModel):
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(..., description="令牌类型")

class TokenVerify(BaseModel):
    valid: bool = Field(..., description="令牌是否有效")

async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """
    解析令牌获取当前用户ID
    
    Args:
        token: JWT令牌
        
    Returns:
        int: 用户ID
        
    Raises:
        HTTPException: 如果令牌无效或过期
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的令牌",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    创建访问令牌
    
    Args:
        data: 要编码到令牌中的数据
        expires_delta: 令牌过期时间
        
    Returns:
        str: JWT令牌
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """注册新用户"""
    try:
        user = await AuthService.create_user(
            username=user_data.username,
            password=user_data.password,
            email=user_data.email,
            phone_number=user_data.phone_number
        )
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """获取访问令牌"""
    user = await AuthService.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    token_data = {
        "sub": user["username"],
        "user_id": user["user_id"],
        "role": "user"  # 默认角色
    }
    access_token = create_access_token(token_data)
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_current_user(user_id: int = Depends(get_current_user_id)):
    """获取当前已登录用户的信息"""
    user = await AuthService.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user

@router.get("/verify", response_model=TokenVerify)
async def verify_token(user_id: int = Depends(get_current_user_id)):
    """验证令牌是否有效"""
    return {"valid": True} 