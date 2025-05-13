from typing import List, Optional, Dict, Any
from dao.specialist_recommendation_dao import get_recommendation_groups

def get_recommendation_service(
    rank: Optional[int] = None,
    province_name: Optional[str] = None,
    subjects: Optional[str] = None,
    limit: int = 1000
) -> List[Dict[str, Any]]:
    try:
        subject_list = [s.strip() for s in subjects.split(',')] if subjects else None
        return get_recommendation_groups(
            rank=rank,
            province_name=province_name,
            subjects=subject_list,
            limit=limit
        )
    except Exception as e:
        print(f"[Service] 获取推荐列表失败: {str(e)}")
        raise e 