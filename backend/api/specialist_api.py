from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from services.specialist_service import SpecialistService
from api.auth_api import get_current_user_id
from utils.logger_utils import setup_logger
from services.profession_service import ProfessionService

# 配置日志
logger = setup_logger(name="specialist_api")

router = APIRouter(prefix="/api/data/specialist", tags=["专家数据"])

class SpecialistFilter(BaseModel):
    """专家数据筛选条件模型"""
    field_name: Optional[str] = Field(None, description="筛选字段名称")
    field_value: Optional[str] = Field(None, description="筛选字段值")

class SpecialistListResponse(BaseModel):
    """专家列表响应模型"""
    data: List[Dict[str, Any]] = Field(..., description="专家数据列表")
    pagination: Dict[str, Any] = Field(..., description="分页信息")

class ScoreRankItem(BaseModel):
    """单个分数排名数据模型"""
    min_score: float = Field(..., description="最低分数")
    max_score: float = Field(..., description="最高分数")
    same_count: int = Field(..., description="同分人数")
    lowest_rank: int = Field(..., description="最低排名")
    highest_rank: int = Field(..., description="最高排名")

class ScoreRankResponse(BaseModel):
    """分数排名响应模型"""
    data: List[ScoreRankItem] = Field(..., description="排名数据列表")
    province_name: str = Field(..., description="省份名称")
    batch: str = Field(..., description="批次")

class EquivalentRankRequest(BaseModel):
    """等效位次请求模型"""
    province_name: str = Field(..., description="省份名称")
    batch: str = Field(..., description="批次")
    score: float = Field(..., description="分数")

class EquivalentRankResponse(BaseModel):
    """等效位次响应模型"""
    rank: int = Field(..., description="等效位次")
    score_range: Dict[str, float] = Field(..., description="分数范围")
    same_count: int = Field(..., description="同分人数")

class ProfessionVersionListResponse(BaseModel):
    """专业版本列表响应模型"""
    code: int = Field(..., description="状态码")
    message: str = Field(..., description="响应消息")
    data: Dict[str, Any] = Field(..., description="响应数据")

@router.get("", response_model=SpecialistListResponse)
async def get_specialists(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数，最多100条"),
    filters: Optional[str] = Query(None, description="筛选条件，JSON格式"),
    province_name: Optional[str] = Query(None, description="省份名称，用于筛选专家所在省份"),
    sort_by: Optional[str] = Query(None, description="排序字段"),
    sort_order: str = Query("DESC", description="排序方向，ASC升序，DESC降序"),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    获取专家数据列表，支持分页、筛选和排序
    
    - **page**: 页码，从1开始
    - **page_size**: 每页条数，最多100条
    - **filters**: 筛选条件，JSON格式，例如：{"name":"张三","age":30}
    - **province_name**: 省份名称，用于筛选专家所在省份
    - **sort_by**: 排序字段，可以是基本字段，也可以是JSON内嵌字段，使用点分隔，例如：name或info.education
    - **sort_order**: 排序方向，ASC升序，DESC降序
    """
    try:
        # 解析过滤条件
        filter_dict = {}
        if filters:
            import json
            try:
                filter_dict = json.loads(filters)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="筛选条件格式错误，请提供有效的JSON"
                )
        
        # 添加省份筛选条件
        if province_name:
            filter_dict["province_name"] = province_name
        
        # 获取专家列表
        result = await SpecialistService.get_specialists(
            page=page,
            page_size=page_size,
            filters=filter_dict,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return result
    except Exception as e:
        logger.error(f"获取专家列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取专家列表失败: {str(e)}"
        )

@router.get("/score-rank", response_model=ScoreRankResponse)
async def get_score_rank(
    province_name: str = Query(..., description="省份名称"),
    year: int = Query(..., description="年份"),
    batch: str = Query("本科", description="批次"),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    获取指定省份、年份的分数排名数据
    
    - **province_name**: 省份名称
    - **year**: 年份
    - **batch**: 批次，默认为"本科"
    """
    try:
        result = await SpecialistService.get_score_rank(
            province_name=province_name,
            year=year,
            batch=batch
        )
        # 使用JSONResponse返回格式化的JSON
        return JSONResponse(
            content=result,
            media_type="application/json",
            status_code=200,
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
    except Exception as e:
        logger.error(f"获取分数排名数据失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分数排名数据失败: {str(e)}"
        )

@router.post("/equivalent-rank", response_model=EquivalentRankResponse)
async def calculate_equivalent_rank(
    request: EquivalentRankRequest,
    current_user_id: int = Depends(get_current_user_id)
):
    """
    计算等效位次
    
    - **province_name**: 省份名称
    - **batch**: 批次
    - **score**: 分数
    """
    try:
        # 获取2024年的数据作为基准
        base_data = await SpecialistService.get_score_rank(
            province_name=request.province_name,
            year=2024,
            batch=request.batch
        )
        
        if not base_data or not base_data.get("data"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未找到2024年的基准数据"
            )
        
        # 对数据进行排序，确保按分数从高到低排序
        sorted_data = sorted(
            base_data["data"],
            key=lambda x: x["minScore"],
            reverse=True
        )
        
        # 处理边界情况
        if request.score > sorted_data[0]["maxScore"]:
            return {
                "rank": sorted_data[0]["lowestRank"],
                "score_range": {
                    "min": sorted_data[0]["minScore"],
                    "max": sorted_data[0]["maxScore"]
                },
                "same_count": sorted_data[0]["sameCount"]
            }
        
        if request.score < sorted_data[-1]["minScore"]:
            return {
                "rank": sorted_data[-1]["highestRank"] + 1,
                "score_range": {
                    "min": sorted_data[-1]["minScore"],
                    "max": sorted_data[-1]["maxScore"]
                },
                "same_count": sorted_data[-1]["sameCount"]
            }
        
        # 二分查找
        left, right = 0, len(sorted_data) - 1
        while left <= right:
            mid = (left + right) // 2
            current_range = sorted_data[mid]
            
            if current_range["minScore"] <= request.score <= current_range["maxScore"]:
                return {
                    "rank": current_range["lowestRank"],
                    "score_range": {
                        "min": current_range["minScore"],
                        "max": current_range["maxScore"]
                    },
                    "same_count": current_range["sameCount"]
                }
            
            if request.score > current_range["maxScore"]:
                right = mid - 1
            else:
                left = mid + 1
        
        # 如果没找到精确匹配，返回最接近的较低分数段
        if left > 0:
            return {
                "rank": sorted_data[left - 1]["lowestRank"],
                "score_range": {
                    "min": sorted_data[left - 1]["minScore"],
                    "max": sorted_data[left - 1]["maxScore"]
                },
                "same_count": sorted_data[left - 1]["sameCount"]
            }
        
        # 如果所有分数段都高于输入分数
        return {
            "rank": sorted_data[-1]["highestRank"] + 1,
            "score_range": {
                "min": sorted_data[-1]["minScore"],
                "max": sorted_data[-1]["maxScore"]
            },
            "same_count": sorted_data[-1]["sameCount"]
        }
        
    except Exception as e:
        logger.error(f"计算等效位次失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"计算等效位次失败: {str(e)}"
        )

@router.get("/colleges")
async def get_college_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    cn_name: Optional[str] = Query(None, description="学校名称，模糊搜索"),
    province_name: Optional[str] = Query(None, description="省份名称，多个用逗号分隔"),
    categories: Optional[str] = Query(None, description="院校类别，多个用逗号分隔"),
    features: Optional[str] = Query(None, description="院校特色，多个用逗号分隔"),
    nature_type: Optional[str] = Query(None, description="院校性质，多个用逗号分隔，public/privite/aw_ga")
) -> Dict[str, Any]:
    """获取大学列表，支持多条件筛选"""
    try:
        # 处理多选参数
        def to_list(val):
            if val is None:
                return None
            if isinstance(val, list):
                return val
            if isinstance(val, str):
                return [v for v in val.split(",") if v]
            return None
        province_list = to_list(province_name)
        categories_list = to_list(categories)
        features_list = to_list(features)
        nature_type_list = to_list(nature_type)
        result = await SpecialistService.get_college_list(
            page=page,
            page_size=page_size,
            cn_name=cn_name,
            province_name=province_list,
            categories=categories_list,
            features=features_list,
            nature_type=nature_type_list
        )
        return {
            "code": 200,
            "message": "获取大学列表成功",
            "data": result
        }
    except Exception as e:
        logger.error(f"获取大学列表失败: {str(e)}")
        return {
            "code": 500,
            "message": f"获取大学列表失败: {str(e)}",
            "data": None
        }

@router.get("/colleges/{code}")
async def get_college_detail(code: str) -> Dict[str, Any]:
    """根据code获取院校详情"""
    try:
        result = await SpecialistService.get_college_detail(code)
        return {
            "code": 200,
            "message": "获取院校详情成功",
            "data": result
        }
    except Exception as e:
        logger.error(f"获取院校详情失败: {str(e)}")
        return {
            "code": 500,
            "message": f"获取院校详情失败: {str(e)}",
            "data": None
        }

@router.get("/profession-versions")
async def get_profession_version_list(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数，最多100条"),
    college_code: Optional[str] = Query(None, description="院校代码"),
    college_name: Optional[str] = Query(None, description="院校名称，模糊搜索"),
    profession_name: Optional[str] = Query(None, description="专业名称，模糊搜索"),
    profession_type: Optional[str] = Query(None, description="专业类"),
    profession_category: Optional[str] = Query(None, description="门类"),
    batch: Optional[str] = Query(None, description="批次"),
    subject_category: Optional[str] = Query(None, description="科类"),
    subject_requirements: Optional[str] = Query(None, description="选科要求"),
    province: Optional[str] = Query(None, description="省份"),
    college_type: Optional[str] = Query(None, description="院校类型"),
    nature_type: Optional[str] = Query(None, description="院校性质"),
    bus_year: Optional[int] = Query(None, description="业务年份"),
    sort_by: Optional[str] = Query(None, description="排序字段"),
    sort_order: str = Query("DESC", description="排序方向，ASC升序，DESC降序"),
    current_user_id: int = Depends(get_current_user_id)
) -> ProfessionVersionListResponse:
    """
    获取专业版本列表，支持多条件筛选
    
    - **page**: 页码，从1开始
    - **page_size**: 每页条数，最多100条
    - **college_code**: 院校代码
    - **college_name**: 院校名称，支持模糊搜索
    - **profession_name**: 专业名称，支持模糊搜索
    - **profession_type**: 专业类
    - **profession_category**: 门类
    - **batch**: 批次
    - **subject_category**: 科类
    - **subject_requirements**: 选科要求
    - **province**: 省份
    - **college_type**: 院校类型
    - **nature_type**: 院校性质
    - **bus_year**: 业务年份
    - **sort_by**: 排序字段
    - **sort_order**: 排序方向，ASC升序，DESC降序
    """
    try:
        # 构建筛选条件
        filters = {}
        if college_code:
            filters["college_code"] = college_code
        if college_name:
            filters["college_name"] = college_name
        if profession_name:
            filters["profession_name"] = profession_name
        if profession_type:
            filters["profession_type"] = profession_type
        if profession_category:
            filters["profession_category"] = profession_category
        if batch:
            filters["batch"] = batch
        if subject_category:
            filters["subject_category"] = subject_category
        if subject_requirements:
            filters["subject_requirements"] = subject_requirements
        if province:
            filters["province"] = province
        if college_type:
            filters["college_type"] = college_type
        if nature_type:
            filters["nature_type"] = nature_type
        if bus_year:
            filters["bus_year"] = bus_year

        # 获取专业版本列表
        result = await SpecialistService.get_profession_version_list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return {
            "code": 200,
            "message": "获取专业版本列表成功",
            "data": result
        }
    except Exception as e:
        logger.error(f"获取专业版本列表失败: {str(e)}")
        return {
            "code": 500,
            "message": f"获取专业版本列表失败: {str(e)}",
            "data": None
        }

@router.get("/profession-groups")
async def get_profession_group_list(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数，最多100条"),
    college_code: Optional[str] = Query(None, description="院校代码"),
    college_name: Optional[str] = Query(None, description="院校名称"),
    profession_group_code: Optional[str] = Query(None, description="专业组代码"),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    获取专业组聚合信息列表
    """
    try:
        from services.specialist_service import SpecialistService
        result = await SpecialistService.get_profession_group_list(
            page=page,
            page_size=page_size,
            college_code=college_code,
            college_name=college_name,
            profession_group_code=profession_group_code
        )
        return {
            "code": 200,
            "message": "获取专业组列表成功",
            "data": result
        }
    except Exception as e:
        logger.error(f"获取专业组列表失败: {str(e)}")
        return {
            "code": 500,
            "message": f"获取专业组列表失败: {str(e)}",
            "data": None
        }

@router.get("/professions")
async def get_profession_list(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数，最多100条"),
    profession_name: Optional[str] = Query(None, description="专业名称，模糊搜索"),
    profession_category: Optional[str] = Query(None, description="专业门类"),
    profession_type: Optional[str] = Query(None, description="专业类"),
    degree_category: Optional[str] = Query(None, description="学位类别"),
    sort_by: Optional[str] = Query(None, description="排序字段"),
    sort_order: str = Query("DESC", description="排序方向，ASC升序，DESC降序"),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    获取专业列表，支持多条件筛选
    
    - **page**: 页码，从1开始
    - **page_size**: 每页条数，最多100条
    - **profession_name**: 专业名称，支持模糊搜索
    - **profession_category**: 专业门类
    - **profession_type**: 专业类
    - **degree_category**: 学位类别
    - **sort_by**: 排序字段
    - **sort_order**: 排序方向，ASC升序，DESC降序
    """
    try:
        # 构建筛选条件
        filters = {}
        if profession_name:
            filters["profession_name"] = profession_name
        if profession_category:
            filters["profession_category"] = profession_category
        if profession_type:
            filters["profession_type"] = profession_type
        if degree_category:
            filters["degree_category"] = degree_category

        # 获取专业列表
        result = await ProfessionService.get_profession_list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return {
            "code": 200,
            "message": "获取专业列表成功",
            "data": result
        }
    except Exception as e:
        logger.error(f"获取专业列表失败: {str(e)}")
        return {
            "code": 500,
            "message": f"获取专业列表失败: {str(e)}",
            "data": None
        }

@router.get("/recommendation")
async def get_recommendation(
    rank: Optional[int] = Query(None, description="分数排名"),
    province_name: Optional[str] = Query(None, description="省份名称"),
    subjects: Optional[str] = Query(None, description="选科要求，逗号分隔")
):
    """
    专业组推荐接口，支持按 rank、province_name、subjects（逗号分隔）筛选
    """
    try:
        from services.specialist_recommendation_service import get_recommendation_service
        records = get_recommendation_service(
            rank=rank,
            province_name=province_name,
            subjects=subjects,
            limit=1000
        )
        return {
            "code": 200,
            "message": "获取推荐列表成功",
            "data": records
        }
    except Exception as e:
        logger.error(f"获取推荐列表失败: {str(e)}")
        return {
            "code": 500,
            "message": f"获取推荐列表失败: {str(e)}",
            "data": None
        }

