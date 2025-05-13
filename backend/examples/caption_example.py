"""
演示如何使用text_captioning模块生成文本说明文字(caption)
"""
import os
import sys

# 添加项目根目录到系统路径，以便导入模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from graph.text_captioning import generate_text_caption

def main():
    # 示例文本
    text = """
    人工智能（AI）是计算机科学的一个分支，它旨在创建能够模拟人类智能的系统。
    这些系统可以学习、推理、感知、规划和解决问题。近年来，随着深度学习技术的发展，
    AI在各个领域取得了显著进步，包括自然语言处理、计算机视觉、机器人技术等。
    """
    
    print("原始文本:")
    print(text)
    print("\n正在生成说明文字...")
    
    # 调用函数生成说明文字
    result = generate_text_caption(text)
    
    print("\n生成的说明文字:")
    print(result["caption"])

if __name__ == "__main__":
    main() 