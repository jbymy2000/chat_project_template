from typing import TypedDict
from langgraph.graph import StateGraph, START
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import asyncio
import json


load_dotenv(override=True)
joke_model = ChatOpenAI(model="gpt-4o")
poem_model = ChatOpenAI(model="gpt-4o")

class State(TypedDict):
    topic: str
    joke: str
    poem: str


async def call_model(state, config):
    topic = state["topic"]
    print("Writing joke...")
    # Note: Passing the config through explicitly is required for python < 3.11
    # Since context var support wasn't added before then: https://docs.python.org/3/library/asyncio-task.html#creating-tasks
    joke_response = await joke_model.ainvoke(
        [{"role": "user", "content": f"Write a joke about {topic}"}],
        config,
    )
    print("\n\nWriting poem...")
    poem_response = await poem_model.ainvoke(
        [{"role": "user", "content": f"Write a short poem about {topic}"}],
        config,
    )
    return {"joke": joke_response.content, "poem": poem_response.content}


graph = StateGraph(State).add_node(call_model).add_edge(START, "call_model").compile()

async def main():
    async for msg, metadata in graph.astream(
        {"topic": "cats"},
        stream_mode="messages",
    ):
        if msg.content:
            print(json.dumps({"content": msg.content}))

if __name__ == "__main__":
    asyncio.run(main())