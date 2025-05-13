from typing import Dict, List, Any, Optional
from dao.clickhouse_db import ClickHouseDB
from utils.logger_utils import setup_logger

logger = setup_logger(name="profession_dao")

class ProfessionDAO:
    """专业数据访问对象，处理与专业数据相关的数据库操作"""
    
    TABLE_NAME = "qihang.dwd_profession_category_info"
    
    @classmethod
    async def get_profession_list(
        cls,
        page: int = 1,
        page_size: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "DESC"
    ) -> Dict[str, Any]:
        """
        获取专业列表数据
        
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
            # 基础查询
            base_query = f"""
            SELECT 
                profession_code,
                profession_name,
                profession_category,
                profession_type,
                degree_category,
                duration,
                establishment_year
            FROM 
                {cls.TABLE_NAME}
            """
            
            # 条件部分
            where_clauses = []
            params = {}
            
            if filters:
                for key, value in filters.items():
                    if key == "profession_name":
                        where_clauses.append("lower(profession_name) LIKE lower(%(profession_name)s)")
                        params["profession_name"] = f"%{value}%"
                    else:
                        where_clauses.append(f"{key} = %({key})s")
                        params[key] = value
            
            # 拼接WHERE子句
            if where_clauses:
                base_query += " WHERE " + " AND ".join(where_clauses)
            
            # 获取总数
            count_query = f"SELECT COUNT(*) as total FROM ({base_query})"
            count_result = ClickHouseDB.execute(count_query, params)
            total = count_result[0]['total'] if count_result else 0
            
            # 排序
            if sort_by:
                base_query += f" ORDER BY {sort_by} {sort_order}"
            
            # 分页
            offset = (page - 1) * page_size
            base_query += f" LIMIT {page_size} OFFSET {offset}"
            
            # 执行查询
            print("[SQL]", base_query)
            print("[PARAMS]", params)
            records = ClickHouseDB.execute(base_query, params)
            
            # 返回结果
            return {
                'items': records,
                'total': total,
                'page': page,
                'page_size': page_size,
                'pages': (total + page_size - 1) // page_size
            }
            
        except Exception as e:
            logger.error(f"获取专业列表失败: {str(e)}")
            raise Exception(f"获取专业列表失败: {str(e)}") 