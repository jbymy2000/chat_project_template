import json
from typing import Dict, List, Any, Optional
import logging
from dao.specialist_dao import SpecialistDAO
from dao.clickhouse_db import ClickHouseDB

# 配置日志
logger = logging.getLogger("specialist_service")

class SpecialistService:
    
    @staticmethod
    async def get_college_list(
        page: int = 1,
        page_size: int = 10,
        cn_name: str = None,
        province_name: list = None,
        categories: list = None,
        features: list = None,
        nature_type: list = None
    ) -> Dict[str, Any]:
        """获取大学列表，支持多条件筛选"""
        try:
            return await SpecialistDAO.get_college_list(
                page=page,
                page_size=page_size,
                cn_name=cn_name,
                province_name=province_name,
                categories=categories,
                features=features,
                nature_type=nature_type
            )
        except Exception as e:
            logger.error(f"获取大学列表失败: {str(e)}")
            raise Exception(f"获取大学列表失败: {str(e)}")
        
    @staticmethod
    async def get_specialists(
        page: int = 1,
        page_size: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "DESC"
    ) -> Dict[str, Any]:
        """
        获取专家列表数据
        
        Args:
            page: 当前页码，从1开始
            page_size: 每页条数
            filters: 筛选条件，键值对
            sort_by: 排序字段
            sort_order: 排序方向，ASC升序，DESC降序
            
        Returns:
            包含数据列表和分页信息的字典
        """
        try:
            # 使用DAO层获取专家列表
            result = await SpecialistDAO.get_specialists(
                page=page,
                page_size=page_size,
                filters=filters,
                sort_by=sort_by,
                sort_order=sort_order
            )
            return result
        except Exception as e:
            logger.error(f"获取专家列表失败: {str(e)}")
            raise Exception(f"获取专家列表失败: {str(e)}")
    
    @staticmethod
    async def get_specialist_by_id(specialist_id: str) -> Dict[str, Any]:
        """
        通过ID获取专家详情
        
        Args:
            specialist_id: 专家ID
            
        Returns:
            专家详情数据
        """
        try:
            # 使用DAO层获取专家详情，默认使用id字段
            specialist = await SpecialistDAO.get_specialist_by_field("id", specialist_id)
            return specialist
        except Exception as e:
            logger.error(f"获取专家详情失败: {str(e)}")
            raise Exception(f"获取专家详情失败: {str(e)}")
            
    @staticmethod
    async def get_specialist_by_field(field_name: str, field_value: str) -> Dict[str, Any]:
        """
        通过指定字段获取专家详情
        
        Args:
            field_name: 字段名称
            field_value: 字段值
            
        Returns:
            专家详情数据
        """
        try:
            # 使用DAO层获取专家详情
            specialist = await SpecialistDAO.get_specialist_by_field(field_name, field_value)
            return specialist
        except Exception as e:
            logger.error(f"获取专家详情失败: {str(e)}")
            raise Exception(f"获取专家详情失败: {str(e)}") 

    @staticmethod
    async def get_score_rank(
        province_name: str,
        year: int,
        batch: str = "本科"
    ) -> Dict[str, Any]:
        """
        获取指定省份、年份的分数排名数据
        
        Args:
            province_name: 省份名称
            year: 年份
            batch: 批次，默认为"本科"
            
        Returns:
            分数排名数据
        """
        try:
            # 使用DAO层获取分数排名数据
            result = await SpecialistDAO.get_score_rank(
                province_name=province_name,
                year=year,
                batch=batch
            )
            if not result:
                return {
                    "province_name": province_name,
                    "batch": batch,
                    "data": []
                }
            return result
        except Exception as e:
            logger.error(f"获取分数排名数据失败: {str(e)}")
            return {
                "province_name": province_name,
                "batch": batch,
                "data": []
            } 

    @staticmethod
    async def get_college_detail(code: str) -> Dict[str, Any]:
        """根据code获取院校详情"""
        try:
            return await SpecialistDAO.get_college_detail(code)
        except Exception as e:
            logger.error(f"获取院校详情失败: {str(e)}")
            raise Exception(f"获取院校详情失败: {str(e)}") 

    @staticmethod
    async def get_profession_version_list(
        page: int,
        page_size: int,
        filters: Dict[str, Any],
        sort_by: Optional[str] = None,
        sort_order: str = "DESC"
    ) -> Dict[str, Any]:
        """
        获取专业版本列表（仅做参数校验和业务拼装，SQL查询交给DAO）
        """
        try:
            # 直接调用DAO层
            return await SpecialistDAO.get_profession_version_list(
                page=page,
                page_size=page_size,
                filters=filters,
                sort_by=sort_by,
                sort_order=sort_order
            )
        except Exception as e:
            logger.error(f"获取专业版本列表失败: {str(e)}")
            return {
                "total": 0,
                "items": [],
                "page": page,
                "page_size": page_size,
                "pages": 0
            } 

    @staticmethod
    async def get_profession_group_list(
        page: int = 1,
        page_size: int = 10,
        college_code: str = None,
        college_name: str = None,
        profession_group_code: str = None
    ) -> dict:
        """
        获取专业组聚合信息列表
        """
        return await SpecialistDAO.get_profession_group_list(
            page=page,
            page_size=page_size,
            college_code=college_code,
            college_name=college_name,
            profession_group_code=profession_group_code
        ) 
            