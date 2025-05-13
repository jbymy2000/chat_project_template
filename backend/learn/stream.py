from typing import TypedDict
from langgraph.graph import StateGraph, START
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
import json
import asyncio
import sys
import os
import traceback

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.chat_openai_reasoning import ChatOpenAIReasoning

load_dotenv(override=True)
print("初始化DeepseekChatOpenAI模型...")
llm = ChatOpenAIReasoning(model="DeepSeek-R1")
print(f"模型初始化完成: {llm.model_name}")

class State(TypedDict):
    topic: str
    joke: str


def refine_topic(state: State):
    print(f"正在处理主题: {state['topic']}")
    refined_topic = state["topic"] + " and cats"
    print(f"处理后的主题: {refined_topic}")
    return {"topic": refined_topic}



def generate_joke(state: State):
    print(f"正在生成关于 '{state['topic']}' 的笑话...")
    try:
        llm_response = llm.invoke(
            [
                HumanMessage(content=f"Generate a joke about {state['topic']}")
            ]
        )
        print(f"笑话生成成功: {llm_response.content}")
        return {"joke": llm_response.content}
    except Exception as e:
        print(f"生成笑话时出错: {str(e)}")
        traceback.print_exc()
        return {"joke": f"Error generating joke: {str(e)}"}


graph = (
    StateGraph(State)
    .add_node(refine_topic)
    .add_node(generate_joke)
    .add_edge(START, "refine_topic")
    .add_edge("refine_topic", "generate_joke")
    .compile()
)

print("开始流处理...")
try:
    message_count = 0
    for msg, metadata in graph.stream({"topic": "ice cream"}, stream_mode="messages"):
        message_count += 1
        print(f"接收到消息 #{message_count}:")
        print(f"消息内容: {msg.content}")
        print(f"消息类型: {type(msg)}")
        print(f"消息additional_kwargs: {msg.additional_kwargs}")
        print(f"消息response_metadata: {msg.response_metadata}")
        print(f"消息id: {msg.id}")
        if hasattr(msg, 'usage_metadata'):
            print(f"消息usage_metadata: {msg.usage_metadata}")
        print(f"元数据: {metadata}")
        print("-" * 50)
    
    if message_count == 0:
        print("没有接收到任何消息!")
except Exception as e:
    print(f"流处理过程中出错: {str(e)}")
    traceback.print_exc()
