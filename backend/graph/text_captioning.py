from typing import Annotated, Dict, Any
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.config import RunnableConfig
import os
import yaml
from dotenv import load_dotenv
from lib.deepseek_chatopenai import DeepseekChatOpenAI
from lib.chat_openai_reasoning import ChatOpenAIReasoning

# 加载环境变量
load_dotenv()

# 确定基础目录路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 加载配置文件
def load_config():
    config_path = os.getenv("CONFIG_PATH", os.path.join(BASE_DIR, "config.yml"))
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"警告: 配置文件 {config_path} 未找到，使用默认配置。")
        return {}

# 获取配置
config = load_config()

class CaptionState(TypedDict):
    messages: Annotated[list, add_messages]
    text: str
    caption: str | None

def generate_caption(state: CaptionState, config: RunnableConfig):
    """
    使用LLM为给定文本生成说明文字(caption)
    """
    caption_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "你是一个专业的文本摘要生成器，负责为用户提出的问题或文本生成简洁的标题或摘要。"
                    "你的任务是：\n"
                    "1. 如果输入是一个问题，提取问题的核心主题作为标题\n"
                    "2. 如果输入是一段文本，提取文本的核心内容作为摘要\n"
                    "生成的标题或摘要应该：\n"
                    "- 长度不超过10个字\n"
                    "- 准确反映原文主题\n"
                    "- 简洁明了，适合作为话题名称\n"
                    "- 保留原文的关键词和实体\n"
                    "请只返回生成的标题或摘要，不要有标点符号，不要有任何解释或额外内容。"
                )
            ),
            ("human", "请为以下文本生成一个简洁的标题或摘要：\n\n{text}")
        ]
    )
    
    text = state["text"]
    
    try:
        # 尝试使用ChatOpenAIReasoning
        llm = ChatOpenAIReasoning(
            model="gpt-4o",
            temperature=0.3,
            streaming=False
        )
    except Exception as e:
        print(f"使用ChatOpenAIReasoning失败: {str(e)}")
        # 如果失败，使用普通的ChatOpenAI
        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            streaming=False
        )
        
    chain = caption_prompt | llm | StrOutputParser()
    
    response = chain.invoke({"text": text})
    
    # 确保结果不为空
    if not response or len(response.strip()) == 0:
        if len(text) <= 10:
            response = text  # 如果原文很短，直接使用原文
        else:
            response = "话题" + str(hash(text) % 1000)  # 使用哈希值生成唯一标识
    
    # 截断过长的结果
    if len(response) > 10:
        response = response[:10]
    
    # 更新状态
    state["caption"] = response
    state["messages"].append({"role": "assistant", "content": response})
    
    return state

def getTextCaptioningGraph():
    """
    创建一个文本说明文字生成的图
    """
    graph = StateGraph(CaptionState)
    
    graph.add_node("generate_caption", generate_caption)
    
    # 添加边
    graph.add_edge(START, "generate_caption")
    graph.add_edge("generate_caption", END)
    
    # 编译图
    return graph.compile()

def generate_text_caption(text: str) -> Dict[str, Any]:
    """
    为给定文本生成说明文字的便捷函数
    
    Args:
        text: 需要生成说明文字的文本
        
    Returns:
        包含生成的说明文字的字典
    """
    graph = getTextCaptioningGraph()
    
    # 初始化状态
    state = {
        "messages": [],
        "text": text,
        "caption": None
    }
    
    # 运行图
    result = graph.invoke(state)
    
    return {
        "caption": result["caption"],
        "text": text
    }
