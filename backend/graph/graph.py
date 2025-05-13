from typing import Annotated

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

# 加载环境变量
load_dotenv()

# 加载配置文件
def load_config():
    config_path = os.getenv("CONFIG_PATH", "config.yml")
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# 获取配置
config = load_config()

class UserInfo(TypedDict):
    province: str
    score: int
    subjects: list[str]
    requirement: str
    

class State(TypedDict):
    messages: Annotated[list, add_messages]
    user_info: UserInfo
    intent: str | None


def requirement_analysis(state: State, config: RunnableConfig):  
    requirement_analysis_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "你是一个负责收集用户关于高考择校需求的调研员。在**用户提问**中，如果用户提出了新的需求，"
                    "请将新需求与**需求列表**中的需求进行融合。如果新需求和旧的某条需求冲突，则更新冲突的信息，不要删除需求条目。"
                    "\n\n当前需求列表： {requirement}\n\n"
                    "\n\n历史对话：\n{messages}\n\n"
                    "\n\n用户提问： {query}\n\n"
                    "请按bullet点列出你处理好的需求列表，格式如下：\n"
                    "- 需求1\n"
                    "- 需求2\n"
                )
            )
        ]
    )
    query = state["messages"][-1].content

    llm = ChatOpenAI(model="gpt-4o")
    chain = requirement_analysis_prompt | llm | StrOutputParser()
    
    if query:
        # 格式化历史消息
        
        response = chain.invoke({
            "query": query, 
            "requirement": state["user_info"]["requirement"],
            "messages": state["messages"]
        })
        state["user_info"]["requirement"] = response
        
        # 保存消息到数据库
    else:
        raise ValueError("query is empty")
    
    return state

def intent_switcher(state: State, config: RunnableConfig):  
    intent_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "你是一个意图分类器，负责判断用户的查询是应该走推荐路径还是闲聊路径。\n"
                    "如果用户查询与高考择校、大学推荐、专业选择、分数分析等相关，则返回'recommender'。\n"
                    "如果用户查询是闲聊、问候、无关高考的话题，则返回'chitchat'。\n"
                    "只返回这两个选项之一，不要有其他内容。\n\n"
                )
            ),
            ("placeholder", "{messages}")
        ]
    )
    
    query = state["messages"][-1].content
    llm = ChatOpenAI(model="gpt-4o")
    chain = intent_prompt | llm | StrOutputParser()
    
    if query:
        # 格式化历史消息
        
        response = chain.invoke({
            "messages": state["messages"]
        })
        intent = response.strip().lower()
        
        if "recommender" in intent:
            state["intent"] = "recommender"
        else:
            state["intent"] = "chitchat"
        
        # 保存消息到数据库
        
        return state
    else:
        raise ValueError("query is empty")

def recommender(state: State, config: RunnableConfig):
    print("recommender")
    recommender_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "你是一个专业的高考择校顾问，负责根据用户的需求和分数推荐合适的大学和专业。\n"
                    "请根据用户的省份、分数、科目和需求，推荐最适合的大学和专业。\n"
                    "推荐时请考虑以下因素：\n"
                    "1. 用户分数与院校录取分数线的匹配度\n"
                    "2. 用户科目与专业要求的匹配度\n"
                    "3. 用户需求与院校特点的匹配度\n"
                    "请给出3-5个推荐选项，每个选项包含院校名称、专业名称、录取概率和推荐理由。\n\n"
                    "历史对话：\n{messages}"
                )
            ),
            ("human", "我的省份是{province}，分数是{score}，科目是{subjects}，需求是{requirement}。请给我推荐合适的大学和专业。")
        ]
    )
    
    user_info = state["user_info"]
    from lib.chat_openai_reasoning import ChatOpenAIReasoning
    llm = ChatOpenAIReasoning(
        model="DeepSeek-R1",
        streaming=True
    )
    chain = recommender_prompt | llm | StrOutputParser()
    
    response = chain.invoke({
        "province": user_info["province"],
        "score": user_info["score"],
        "subjects": ", ".join(user_info["subjects"]),
        "requirement": user_info["requirement"],
        "messages": state["messages"]
    })
    
    state["messages"].append({"role": "assistant", "content": response})
    return state

def chitchat(state: State, config: RunnableConfig): 
    print("chitchat")
    chitchat_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "你是一个友好的高考择校助手，负责回答用户的闲聊问题。\n"
                    "请用简洁、友好的语气回答用户的问题，不要过于正式。\n"
                    "如果用户询问与高考无关的话题，可以适当引导回高考择校相关话题。\n\n"
                )
            ),
            ("placeholder", "{messages}")
        ]
    )
    
    from lib.chat_openai_reasoning import ChatOpenAIReasoning
    llm = ChatOpenAIReasoning(
        model="DeepSeek-R1",
        streaming=True
    )
    chain = chitchat_prompt | llm | StrOutputParser()
    
    response = chain.invoke({
        "messages": state["messages"]
    })
    
    state["messages"].append({"role": "assistant", "content": response})
    return state

def getGraph():
    graph = StateGraph(State)
    
    graph.add_node("requirement_analysis", requirement_analysis)
    graph.add_node("intent_switcher", intent_switcher)
    graph.add_node("recommender", recommender)
    graph.add_node("chitchat", chitchat)
    
    # 添加边
    graph.add_edge(START, "requirement_analysis")
    graph.add_edge("requirement_analysis", "intent_switcher")
    
    # 添加条件边
    graph.add_conditional_edges(
        "intent_switcher",
        lambda x: x["intent"],
        {
            "recommender": "recommender",
            "chitchat": "chitchat"
        }
    )
    
    # 添加结束边
    graph.add_edge("chitchat", END)
    graph.add_edge("recommender", END)
    
    # 使用streaming=True参数编译图，确保支持异步迭代
    return graph.compile()