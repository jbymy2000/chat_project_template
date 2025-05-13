from typing import Dict, Any, List
from datetime import datetime

def format_datetime(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    将字典中的datetime对象转换为ISO格式字符串
    
    Args:
        data: 待处理的字典数据
        
    Returns:
        Dict[str, Any]: 处理后的字典，datetime对象被转换为ISO格式字符串
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, datetime):
            result[key] = value.isoformat()
        else:
            result[key] = value
    return result

def format_datetime_list(data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    处理列表中每个字典的datetime对象，转换为ISO格式字符串
    
    Args:
        data_list: 字典列表
        
    Returns:
        List[Dict[str, Any]]: 处理后的字典列表
    """
    return [format_datetime(item) for item in data_list] 