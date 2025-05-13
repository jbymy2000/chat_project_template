#!/usr/bin/env python
"""
测试话题摘要生成和创建功能
"""
import os
import sys
import asyncio
from typing import Dict, Any
import time

# 确定项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 添加项目根目录到系统路径
sys.path.insert(0, BASE_DIR)

from services.topic_service import TopicService
from graph.text_captioning import generate_text_caption


async def test_generate_caption():
    """测试直接生成摘要"""
    print("=== 测试直接生成摘要 ===")
    
    test_cases = [
        "我的高考志愿应该怎么填？我的分数是560分，文科，想学经济类专业。",
        "北京大学的计算机科学专业怎么样？",
        "清华和北大哪个更适合学习物理？",
        "我想了解一下南方的大学有哪些比较好的",
        "高考575分能上什么大学？"
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n测试案例 {i}: {text}")
        
        start_time = time.time()
        result = generate_text_caption(text)
        end_time = time.time()
        
        print(f"生成的摘要: {result['caption']}")
        print(f"生成耗时: {end_time - start_time:.2f}秒")


async def test_service_generate_caption():
    """测试服务层生成摘要"""
    print("\n=== 测试服务层生成摘要 ===")
    
    test_cases = [
        "我的高考志愿应该怎么填？我的分数是560分，文科，想学经济类专业。",
        "北京大学的计算机科学专业怎么样？",
        "清华和北大哪个更适合学习物理？",
        "我想了解一下南方的大学有哪些比较好的",
        "高考575分能上什么大学？"
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n测试案例 {i}: {text}")
        
        start_time = time.time()
        result = await TopicService.generate_topic_caption(text)
        end_time = time.time()
        
        print(f"生成的摘要: {result}")
        print(f"生成耗时: {end_time - start_time:.2f}秒")


async def test_create_topic_with_caption():
    """测试创建带摘要的话题（模拟）"""
    print("\n=== 测试创建带摘要的话题（模拟） ===")
    
    # 模拟用户ID
    user_id = 1
    
    # 模拟TopicDAO.create_topic方法
    async def mock_create_topic(user_id, topic):
        return {
            "topic_id": 123,
            "user_id": user_id,
            "topic": topic,
            "started_at": "2023-05-01 10:00:00",
            "updated_at": "2023-05-01 10:00:00"
        }
    
    # 模拟MessageService.create_message方法
    async def mock_create_message(topic_id, user_id, message_type, content):
        return {
            "message_id": 456,
            "topic_id": topic_id,
            "user_id": user_id,
            "message_type": message_type,
            "content": content,
            "created_at": "2023-05-01 10:00:00"
        }
    
    # 替换真实方法为模拟方法
    import unittest.mock as mock
    from dao.topic_dao import TopicDAO
    from services.message_service import MessageService
    
    original_create_topic = TopicDAO.create_topic
    original_create_message = MessageService.create_message
    
    TopicDAO.create_topic = mock_create_topic
    MessageService.create_message = mock_create_message
    
    try:
        # 测试用例
        test_cases = [
            "我的高考志愿应该怎么填？我的分数是560分，文科，想学经济类专业。",
            "北京大学的计算机科学专业怎么样？",
        ]
        
        for i, text in enumerate(test_cases, 1):
            print(f"\n测试案例 {i}: {text}")
            
            # 测试使用摘要
            start_time = time.time()
            result = await TopicService.create_topic_with_caption(user_id, text, True)
            end_time = time.time()
            
            print(f"使用摘要 - 话题名称: {result['topic']}")
            print(f"处理耗时: {end_time - start_time:.2f}秒")
            
            # 测试不使用摘要
            start_time = time.time()
            result = await TopicService.create_topic_with_caption(user_id, text, False)
            end_time = time.time()
            
            print(f"不使用摘要 - 话题名称: {result['topic']}")
            print(f"处理耗时: {end_time - start_time:.2f}秒")
    
    finally:
        # 恢复原始方法
        TopicDAO.create_topic = original_create_topic
        MessageService.create_message = original_create_message


async def main():
    """主函数"""
    print(f"Python版本: {sys.version}")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"项目根目录: {BASE_DIR}\n")
    
    # 测试直接生成摘要
    await test_generate_caption()
    
    # 测试服务层生成摘要
    await test_service_generate_caption()
    
    # 测试创建带摘要的话题
    await test_create_topic_with_caption()


if __name__ == "__main__":
    asyncio.run(main()) 