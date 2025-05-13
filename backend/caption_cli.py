#!/usr/bin/env python
"""
文本生成说明文字(caption)的命令行工具
"""
import os
import sys
import argparse
import time

# 确定项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 添加项目根目录到系统路径
sys.path.insert(0, BASE_DIR)

from graph.text_captioning import generate_text_caption


def generate_caption_for_text(text, verbose=False):
    """为文本生成说明文字"""
    if verbose:
        print("输入文本:")
        print("-" * 40)
        print(text)
        print("-" * 40)
        print("\n正在生成说明文字...")
    
    start_time = time.time()
    
    try:
        # 调用函数
        result = generate_text_caption(text)
        
        end_time = time.time()
        
        if verbose:
            print("\n生成结果:")
            print("-" * 40)
        
        print(f"说明文字: {result['caption']}")
        
        if verbose:
            print(f"长度: {len(result['caption'])}个字")
            print(f"生成耗时: {end_time - start_time:.2f}秒")
        
        return result["caption"]
    
    except Exception as e:
        print(f"错误: {str(e)}")
        return None


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="文本生成说明文字(caption)的命令行工具")
    parser.add_argument("--file", "-f", help="包含文本的文件路径")
    parser.add_argument("--text", "-t", help="需要生成说明文字的文本")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细信息")
    
    args = parser.parse_args()
    
    if not args.file and not args.text:
        print("请提供文本或文件路径")
        parser.print_help()
        return 1
    
    # 从文件或命令行参数获取文本
    text = ""
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            print(f"读取文件失败: {str(e)}")
            return 1
    else:
        text = args.text
    
    # 生成说明文字
    generate_caption_for_text(text, args.verbose)
    
    return 0


if __name__ == "__main__":
    # 打印环境信息
    print(f"Python版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    print(f"项目根目录: {BASE_DIR}")
    print()
    
    sys.exit(main()) 