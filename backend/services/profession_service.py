from typing import Dict, List, Any, Optional
from dao.profession_dao import ProfessionDAO
from utils.logger_utils import setup_logger

logger = setup_logger(name="profession_service")

class ProfessionService:
    def __init__(self):
        self.dao = ProfessionDAO()

    @staticmethod
    async def get_profession_list(
        page: int = 1,
        page_size: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "DESC"
    ) -> Dict[str, Any]:
        """
        获取专业列表
        
        Args:
            page: 页码，从1开始
            page_size: 每页条数
            filters: 筛选条件
            sort_by: 排序字段
            sort_order: 排序方向，ASC或DESC
            
        Returns:
            Dict包含分页信息和数据列表
        """
        try:
            # 参数验证
            if page < 1:
                page = 1
            if page_size < 1 or page_size > 100:
                page_size = 10
            if sort_order not in ["ASC", "DESC"]:
                sort_order = "DESC"

            # 调用DAO层获取数据
            result = await ProfessionService().dao.get_profession_list(
                page=page,
                page_size=page_size,
                filters=filters,
                sort_by=sort_by,
                sort_order=sort_order
            )

            return result

        except Exception as e:
            logger.error(f"获取专业列表失败: {str(e)}")
            raise e 