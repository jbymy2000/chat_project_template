import json
from typing import Dict, List, Any, Optional
import logging
from dao.clickhouse_db import ClickHouseDB
from dao.database import Database

# 配置日志
logger = logging.getLogger("specialist_dao")

class SpecialistDAO:
    """专家数据访问对象，处理与专家数据相关的数据库操作"""
    
    TABLE_NAME = "qihang.dwd_tszh_specialist_fat"
    
    @classmethod
    async def get_specialists(
        cls,
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
            # 基础查询
            base_query = f"""
            SELECT 
                record_value,
                dt,
                file_name,
                province_name
            FROM 
                {cls.TABLE_NAME}
            """
            
            # 条件部分
            where_clauses = []
            params = {}
            
            if filters:
                # 提取province_name进行特殊处理
                province_name = filters.pop('province_name', None)
                
                # 构建JSON条件查询
                for key, value in filters.items():
                    # 对JSON字段内的值处理
                    if value is not None and value != "":
                        # 添加JSON字段条件，使用JSONExtractString函数
                        param_name = f"param_{len(params)}"
                        where_clauses.append(f"JSONExtractString(record_value, '{key}') = {{{param_name}:String}}")
                        params[param_name] = str(value)
                
                # 处理province_name作为表字段
                if province_name is not None and province_name != "":
                    param_name = f"param_{len(params)}"
                    where_clauses.append(f"province_name = {{{param_name}:String}}")
                    params[param_name] = str(province_name)
            
            # 拼接WHERE子句
            if where_clauses:
                base_query += " WHERE " + " AND ".join(where_clauses)
            
            # 获取总数
            count_query = f"SELECT COUNT(*) as total FROM ({base_query})"
            count_result = ClickHouseDB.execute(count_query, params)
            total = count_result[0]['total'] if count_result else 0
            
            # 排序
            if sort_by:
                # 如果是JSON内的字段，需要使用JSONExtract函数
                if "." in sort_by:
                    field_parts = sort_by.split(".")
                    if len(field_parts) == 2:
                        sort_clause = f"JSONExtractString(record_value, '{field_parts[1]}')"
                    else:
                        # 多层嵌套
                        parent = field_parts[0]
                        for i in range(1, len(field_parts) - 1):
                            parent = f"JSONExtractRaw(record_value, '{parent}')"
                        sort_clause = f"JSONExtractString({parent}, '{field_parts[-1]}')"
                else:
                    # 非JSON字段直接排序
                    sort_clause = sort_by
                
                base_query += f" ORDER BY {sort_clause} {sort_order}"
            else:
                # 默认排序
                base_query += f" ORDER BY dt DESC"
            
            # 分页
            offset = (page - 1) * page_size
            base_query += f" LIMIT {page_size} OFFSET {offset}"
            
            # 执行查询
            records = ClickHouseDB.execute(base_query, params)
            
            # 处理结果，将JSON字符串转为字典
            specialists = []
            for record in records:
                try:
                    # 解析JSON并与基础数据合并
                    record_data = json.loads(record['record_value'])
                    # 添加非JSON字段
                    record_data.update({
                        'dt': record['dt'].isoformat() if record['dt'] else None,
                        'file_name': record['file_name'],
                        'province_name': record['province_name']
                    })
                    specialists.append(record_data)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析错误: {str(e)}, record_value: {record['record_value']}")
                    # 如果JSON解析失败，仍添加原始数据
                    specialists.append({
                        'record_value': record['record_value'],
                        'dt': record['dt'].isoformat() if record['dt'] else None,
                        'file_name': record['file_name'],
                        'province_name': record['province_name'],
                        'parse_error': str(e)
                    })
            
            # 返回结果
            return {
                'data': specialists,
                'pagination': {
                    'total': total,
                    'page': page,
                    'page_size': page_size,
                    'pages': (total + page_size - 1) // page_size
                }
            }
            
        except Exception as e:
            logger.error(f"获取专家列表失败: {str(e)}")
            raise Exception(f"获取专家列表失败: {str(e)}")
    
    @classmethod
    async def get_specialist_by_field(
        cls, 
        field_name: str,
        field_value: str
    ) -> Dict[str, Any]:
        """
        通过指定字段查询专家详情
        
        Args:
            field_name: 字段名称
            field_value: 字段值
            
        Returns:
            专家详情数据
        """
        try:
            # 处理特殊表字段
            if field_name == "province_name":
                where_clause = f"province_name = {{value:String}}"
            # 判断是否是JSON内部字段
            elif "." in field_name:
                # JSON内部字段，使用JSONExtractString
                parts = field_name.split(".")
                if len(parts) == 2:
                    where_clause = f"JSONExtractString(record_value, '{parts[1]}') = {{value:String}}"
                else:
                    # 先不处理过于复杂的嵌套结构
                    raise Exception(f"不支持超过2级的嵌套JSON字段: {field_name}")
            else:
                # 普通字段或JSON第一级字段
                where_clause = f"JSONExtractString(record_value, '{field_name}') = {{value:String}}"
            
            query = f"""
            SELECT 
                record_value,
                dt,
                file_name,
                province_name
            FROM 
                {cls.TABLE_NAME}
            WHERE
                {where_clause}
            LIMIT 1
            """
            
            params = {'value': field_value}
            records = ClickHouseDB.execute(query, params)
            
            if not records:
                raise Exception(f"未找到{field_name}为 {field_value} 的专家数据")
            
            record = records[0]
            try:
                # 解析JSON并与基础数据合并
                record_data = json.loads(record['record_value'])
                # 添加非JSON字段
                record_data.update({
                    'dt': record['dt'].isoformat() if record['dt'] else None,
                    'file_name': record['file_name'],
                    'province_name': record['province_name']
                })
                return record_data
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析错误: {str(e)}, record_value: {record['record_value']}")
                # 如果JSON解析失败，仍返回原始数据
                return {
                    'record_value': record['record_value'],
                    'dt': record['dt'].isoformat() if record['dt'] else None,
                    'file_name': record['file_name'],
                    'province_name': record['province_name'],
                    'parse_error': str(e)
                }
                
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
        从数据库获取分数排名数据
        
        Args:
            province_name: 省份名称
            year: 年份
            batch: 批次，默认为"本科"
            
        Returns:
            分数排名数据
        """
        try:
            query = """
            SELECT 
                ranks,
                province_name,
                batch
            FROM dwd_youzy_score_rank_chunk 
            WHERE province_name = %(province_name)s 
            AND year = %(year)s 
            AND batch = %(batch)s
            LIMIT 1
            """
            
            params = {
                "province_name": province_name,
                "year": year,
                "batch": batch
            }
            
            result = ClickHouseDB.execute(query, params)
            if not result or len(result) == 0:
                return None
                
            # 解析ranks字段（JSON字符串）
            try:
                first_row = result[0]
                ranks_data = json.loads(first_row['ranks'])
                if not isinstance(ranks_data, list) or len(ranks_data) == 0:
                    raise Exception("ranks字段解析结果不是有效的列表或列表为空")
                    
                return {
                    "data": ranks_data,
                    "province_name": first_row['province_name'],
                    "batch": first_row['batch']
                }
            except json.JSONDecodeError as e:
                logger.error(f"解析ranks字段失败: {str(e)}")
                raise Exception(f"解析ranks字段失败: {str(e)}")
            except Exception as e:
                logger.error(f"处理查询结果失败: {str(e)}")
                raise Exception(f"处理查询结果失败: {str(e)}")
                
        except Exception as e:
            logger.error(f"从数据库获取分数排名数据失败: {str(e)}")
            raise Exception(f"从数据库获取分数排名数据失败: {str(e)}")

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
            where_clauses = []
            params = {}
            # cn_name模糊搜索
            if cn_name:
                where_clauses.append("lower(cn_name) LIKE lower(%(cn_name)s)")
                params["cn_name"] = f"%{cn_name}%"
            # province_name多选
            if province_name:
                province_list = [p for p in province_name if p]
                if province_list:
                    province_sql = ','.join([f"'{p}'" for p in province_list])
                    where_clauses.append(f"province_name IN ({province_sql})")
            # nature_type多选
            if nature_type:
                nature_list = [n for n in nature_type if n]
                if nature_list:
                    nature_sql = ','.join([f"'{n}'" for n in nature_list])
                    where_clauses.append(f"nature_type IN ({nature_sql})")
            # categories数组筛选（hasAny实现）
            if categories:
                where_clauses.append("hasAny(categories, %(categories_any)s)")
                params["categories_any"] = categories
            # features数组筛选（hasAny实现）
            if features:
                where_clauses.append("hasAny(features, %(features_any)s)")
                params["features_any"] = features
            # 拼接where
            where_sql = ""
            if where_clauses:
                where_sql = "WHERE " + " AND ".join(where_clauses)
            # 统计总数
            count_query = f"SELECT count(*) as total FROM qihang.dwd_youzy_college_info {where_sql}"
            count_result = ClickHouseDB.execute(count_query, params)
            total = count_result[0]['total'] if count_result else 0
            # 分页数据
            offset = (page - 1) * page_size
            query = f"""
            SELECT 
                id,
                num_id,
                code,
                gb_code,
                cn_name,
                logo_url,
                province_name,
                city_name,
                nature_type,
                edu_level,
                categories,
                features,
                introduction,
                en_name,
                short_name,
                motto,
                number_of_stu,
                male_rate_of_stu,
                female_rate_of_stu,
                rate_of_baoyan,
                star,
                ranking_of_wsl,
                ranking_of_rk,
                ranking_of_xyh,
                ranking_of_us_news,
                ranking_of_qs,
                ranking_of_edu,
                web_site,
                zhao_ban_wz,
                zhao_ban_dh,
                updated_at
            FROM qihang.dwd_youzy_college_info
            {where_sql}
            ORDER BY updated_at DESC
            LIMIT {page_size} OFFSET {offset}
            """
            print("[SQL]", query)
            print("[PARAMS]", params)
            records = ClickHouseDB.execute(query, params)
            colleges = []
            for record in records:
                if 'categories' in record and isinstance(record['categories'], str):
                    try:
                        record['categories'] = eval(record['categories'])
                    except:
                        record['categories'] = []
                if 'features' in record and isinstance(record['features'], str):
                    try:
                        record['features'] = eval(record['features'])
                    except:
                        record['features'] = []
                colleges.append(dict(record))
            return {
                "total": total,
                "items": colleges
            }
        except Exception as e:
            logger.error(f"获取大学列表失败: {str(e)}")
            raise Exception(f"获取大学列表失败: {str(e)}")

    @staticmethod
    async def get_college_detail(code: str) -> Dict[str, Any]:
        """根据code获取院校详情"""
        try:
            query = """
            SELECT * FROM qihang.dwd_youzy_college_info WHERE code = %(code)s LIMIT 1
            """
            params = {"code": code}
            records = ClickHouseDB.execute(query, params)
            if not records:
                return {}
            record = records[0]
            # 处理数组类型字段
            if 'categories' in record and isinstance(record['categories'], str):
                try:
                    record['categories'] = eval(record['categories'])
                except:
                    record['categories'] = []
            if 'features' in record and isinstance(record['features'], str):
                try:
                    record['features'] = eval(record['features'])
                except:
                    record['features'] = []
            return dict(record)
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
        获取专业版本列表
        """
        try:
            query = """
                SELECT 
                    bus_year,
                    college_code,
                    college_name,
                    profession_group_code,
                    profession_enroll_code,
                    profession_name,
                    profession_type,
                    profession_category,
                    batch,
                    subject_category,
                    subject_requirements,
                    plan_num,
                    study_duration,
                    tuition,
                    last_4_year_avg_rank,
                    last_4_year_avg_score,
                    last_3_year_avg_rank,
                    last_3_year_avg_score,
                    last_2_year_avg_rank,
                    last_2_year_avg_score,
                    last_1_year_avg_rank,
                    last_1_year_avg_score,
                    profession_standard,
                    profession_evaluation,
                    doctoral_program,
                    master_program,
                    rk_rank,
                    rk_rating,
                    baoyan_rate,
                    nature_type,
                    college_location,
                    city_level,
                    province,
                    education_level,
                    college_type,
                    college_ranking,
                    college_tags,
                    college_level,
                    belong_to
                FROM qihang.dwm_tszh_specialistversion_fat
                WHERE 1=1
            """
            params = []
            if filters:
                for key, value in filters.items():
                    if key in ["college_name", "profession_name"]:
                        query += f" AND {key} LIKE %s"
                        params.append(f"%{value}%")
                    else:
                        query += f" AND {key} = %s"
                        params.append(value)
            # 打印SQL和参数
            print("[ProfessionVersion SQL]", query)
            print("[ProfessionVersion PARAMS]", params)
            count_query = f"SELECT COUNT(*) as total FROM ({query}) as t"
            total_result = ClickHouseDB.execute(count_query, params)
            total = total_result[0]["total"] if total_result else 0
            if sort_by:
                query += f" ORDER BY {sort_by} {sort_order}"
            else:
                query += " ORDER BY bus_year DESC, college_code ASC"
            offset = (page - 1) * page_size
            query += f" LIMIT {page_size} OFFSET {offset}"
            # 再次打印最终SQL
            print("[ProfessionVersion SQL FINAL]", query)
            items = ClickHouseDB.execute(query, params)
            return {
                "total": total,
                "items": items,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size
            }
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
        聚合查询专业组信息，支持分页和基础筛选
        """
        try:
            where_clauses = []
            params = {}
            if college_code:
                where_clauses.append("college_code = %(college_code)s")
                params["college_code"] = college_code
            if college_name:
                where_clauses.append("college_name = %(college_name)s")
                params["college_name"] = college_name
            if profession_group_code:
                where_clauses.append("profession_group_code = %(profession_group_code)s")
                params["profession_group_code"] = profession_group_code
            where_sql = ""
            if where_clauses:
                where_sql = "WHERE " + " AND ".join(where_clauses)
            # 聚合SQL
            base_query = f'''
                SELECT  college_code,
                        college_name,
                        profession_group_code,
                        profession_group_plan_num,
                        subject_requirements,
                        college_tags,
                        min(last_1_year_min_rank) as last_1_year_min_rank,
                        min(last_1_year_min_score) as last_1_year_min_score,
                        min(last_2_year_min_rank) as last_2_year_min_rank,
                        min(last_2_year_min_score) as last_2_year_min_score,
                        min(last_3_year_min_rank) as last_3_year_min_rank,
                        min(last_3_year_min_score) as last_3_year_min_score
                FROM qihang.dwm_tszh_specialistversion_fat
                {where_sql}
                GROUP BY college_code, college_name, profession_group_code, profession_group_plan_num, subject_requirements, college_tags
            '''
            # 统计总数
            count_query = f"SELECT count() as total FROM (SELECT 1 FROM qihang.dwm_tszh_specialistversion_fat {where_sql} GROUP BY college_code, college_name, profession_group_code, profession_group_plan_num, subject_requirements, college_tags)"
            count_result = ClickHouseDB.execute(count_query, params)
            total = count_result[0]["total"] if count_result else 0
            # 分页
            offset = (page - 1) * page_size
            query = base_query + f" LIMIT {page_size} OFFSET {offset}"
            print("[ProfessionGroup SQL]", query)
            print("[ProfessionGroup PARAMS]", params)
            items = ClickHouseDB.execute(query, params)
            return {
                "total": total,
                "items": items,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size
            }
        except Exception as e:
            logger.error(f"获取专业组列表失败: {str(e)}")
            return {
                "total": 0,
                "items": [],
                "page": page,
                "page_size": page_size,
                "pages": 0
            } 