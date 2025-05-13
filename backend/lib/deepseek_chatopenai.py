import asyncio
from typing import Any, Optional, Iterator
from typing import AsyncIterator

from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain_core.messages import AIMessageChunk
from langchain_core.outputs import ChatGenerationChunk, LLMResult
from langchain_openai import ChatOpenAI


class DeepseekChatOpenAI(ChatOpenAI):
    async def _astream(
            self,
            messages: Any,
            stop: Optional[Any] = None,
            run_manager: Optional[Any] = None,
            **kwargs: Any,
    ) -> AsyncIterator[AIMessageChunk]:
        openai_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                openai_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                openai_messages.append({"role": "assistant", "content": msg.content})
            elif isinstance(msg, SystemMessage):
                openai_messages.append({"role": "system", "content": msg.content})
            else:
                raise ValueError(f"Unsupported message type: {type(msg)}")

        params = {
            "model": self.model_name,
            "messages": openai_messages,
            **self.model_kwargs,
            **kwargs,
            "extra_body": {
                "enable_enhanced_generation": True,
                **(kwargs.get("extra_body", {})),
                **(self.model_kwargs.get("extra_body", {}))
            }
        }
        params = {k: v for k, v in params.items() if v not in (None, {}, [])}

        # Create and process the stream
        async for chunk in await self.async_client.create(
                stream=True,
                **params
        ):
            # 添加安全检查，防止空列表导致IndexError
            if not chunk.choices or len(chunk.choices) == 0:
                continue
                
            content = chunk.choices[0].delta.content or ""
            reasoning = ""
            if hasattr(chunk.choices[0].delta, "model_extra") and chunk.choices[0].delta.model_extra:
                reasoning = chunk.choices[0].delta.model_extra.get("reasoning_content", "")
                print(f"DEBUG - 原始reasoning数据: {reasoning}")
                
            if content:
                chunk_msg = AIMessageChunk(content=content)
                # 添加类型标记
                chunk_msg.type = "content"
                print(f"DEBUG - content chunk_msg: {chunk_msg}")
                yield ChatGenerationChunk(
                    message=chunk_msg,
                    generation_info={"token_type": "content", "reasoning": reasoning if reasoning else None}
                )
            if reasoning:
                reasoning_msg = AIMessageChunk(
                    content="",
                    additional_kwargs={"reasoning": reasoning, "token_type": "reasoning"}
                )
                # 添加类型标记
                reasoning_msg.type = "reasoning"
                print(f"DEBUG - reasoning chunk_msg: {reasoning_msg}")
                yield ChatGenerationChunk(
                    message=reasoning_msg,
                    generation_info={"token_type": "reasoning", "reasoning": reasoning}
                )

    def invoke(
            self,
            messages: Any,
            stop: Optional[Any] = None,
            run_manager: Optional[Any] = None,
            **kwargs: Any,
    ) -> AIMessage:
        async def _ainvoke():
            combined_content = []
            combined_reasoning = []
            async for chunk in self._astream(messages, stop, run_manager, **kwargs):
                if chunk.message.content:
                    combined_content.append(chunk.message.content)
                # If reasoning is in additional_kwargs, gather that too
                if "reasoning" in chunk.message.additional_kwargs:
                    print(f"DEBUG - invoke方法收集additional_kwargs中的reasoning: {chunk.message.additional_kwargs['reasoning']}")
                    combined_reasoning.append(
                        chunk.message.additional_kwargs["reasoning"]
                    )
            
            print(f"DEBUG - invoke方法combined_reasoning最终长度: {len(combined_reasoning)}")
            final_msg = AIMessage(
                content="".join(combined_content),
                additional_kwargs={"reasoning": "".join(combined_reasoning)} if combined_reasoning else {}
            )
            print(f"DEBUG - invoke方法返回的final_msg: {final_msg}")
            return final_msg

        return asyncio.run(_ainvoke())