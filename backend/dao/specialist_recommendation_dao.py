from typing import List, Optional, Dict, Any
from dao.clickhouse_db import ClickHouseDB

def get_recommendation_groups(
    rank: Optional[int] = None,
    province_name: Optional[str] = None,
    subjects: Optional[List[str]] = None,
    limit: int = 1000
) -> List[Dict[str, Any]]:
    where_clauses = []
    params = {}
    if subjects:
        where_clauses.append("hasAll(subject_requirements_clean, %(subjects)s)")
        params["subjects"] = list(subjects)
    if province_name:
        where_clauses.append("province = %(province_name)s")
        params["province_name"] = province_name
    where_sql = ""
    if where_clauses:
        where_sql = "WHERE " + " AND ".join(where_clauses)
    having_sql = ""
    if rank is not None:
        # 默认区间：rank-2000 ~ rank+10000
        having_sql = "HAVING last_2_year_min_rank BETWEEN %(rank_2_min)s AND %(rank_2_max)s"
        params["rank_2_min"] = rank - 2000
        params["rank_2_max"] = rank + 10000
    sql = f"""
        SELECT
            college_code,
            college_name,
            profession_group_code,
            profession_group_plan_num,
            subject_requirements,
            college_tags,
            city_level,
            min(last_1_year_min_rank) as last_1_year_min_rank,
            min(last_1_year_min_score) as last_1_year_min_score,
            min(last_2_year_min_rank) as last_2_year_min_rank,
            min(last_2_year_min_score) as last_2_year_min_score,
            min(last_3_year_min_rank) as last_3_year_min_rank,
            min(last_3_year_min_score) as last_3_year_min_score
        FROM qihang.dwm_tszh_specialistversion_fat
        {where_sql}
        GROUP BY college_code,
                 college_name,
                 profession_group_code,
                 profession_group_plan_num,
                 subject_requirements,
                 college_tags,
                 city_level
        {having_sql}
        LIMIT {limit}
    """
    print("[SQL]", sql)
    print("[PARAMS]", params)
    return ClickHouseDB.execute(sql, params) 