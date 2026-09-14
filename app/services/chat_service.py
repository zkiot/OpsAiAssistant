import logging

from app.infrastructure.llm.base import LLMClient
from app.infrastructure.llm.deepseek_client import DeepSeekClient
from app.schemas.chat import ChatResponse
from app.services.memory_service import MemoryService
from app.services.rag_service import RAGService
from app.infrastructure.mcp.mcp_client import MCPToolClient, mcp_tools_to_openai_schema
from collections.abc import AsyncGenerator
from typing import Any
import time
import json

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = "你是一个专业的运维助手，基于提供的知识库内容回答问题，不要编造知识库中没有的信息。"
MAX_TOOL_ITERATIONS = 6  # 防止死循环/过度调用，对应之前提到的"最大调用链路"控制


class ChatService:
    """应用层：编排"检索知识库 + 组装历史对话 + 调用LLM生成回复"这条业务流程。
    本身不含具体的检索/存储实现细节，那些在 RAGService / MemoryService 里。
    """

    def __init__(
            self,
            llm_client: LLMClient | None = None,
            rag_service: RAGService | None = None,
            memory_service: MemoryService | None = None,
            mcp_client: MCPToolClient | None = None,
    ):
        self._llm = llm_client or DeepSeekClient()
        self._rag = rag_service or RAGService()
        self._memory = memory_service or MemoryService()
        self._mcp = mcp_client

    async def ask_with_tools(self, session_id: str, question: str) -> ChatResponse:
        if self._mcp is None:
            return await self.ask(session_id, question)  # 没配置MCP，退化成普通RAG问答
        start = time.time()
        tools_schema = mcp_tools_to_openai_schema(await self._mcp.list_tools())
        history = await self._memory.get_history(session_id)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *history,
            {"role": "user", "content": question},
        ]

        used_sources: list[str] = []
        seen_calls: set[str] = set()  # 用于检测重复调用，防止模型在同一参数上死循环
        answer = ""

        for step in range(MAX_TOOL_ITERATIONS):
            response = await self._llm.chat(messages, tools=tools_schema)

            if not response.has_tool_calls:
                answer = response.content or ""
                break

            # 把模型的调用意图加入历史（DeepSeek/OpenAI 要求这样格式的assistant消息）
            messages.append({
                "role": "assistant",
                "content": response.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.name, "arguments": json.dumps(tc.arguments, ensure_ascii=False)},
                    }
                    for tc in response.tool_calls
                ],
            })

            for tc in response.tool_calls:
                call_signature = f"{tc.name}:{json.dumps(tc.arguments, sort_keys=True)}"
                if call_signature in seen_calls:
                    # 同一个工具、同一组参数重复调用，直接提示模型换个方式，避免死循环
                    tool_result = "该工具已用相同参数调用过，请基于已有结果直接回答，不要重复调用。"
                else:
                    seen_calls.add(call_signature)
                    try:
                        tool_result = await self._mcp.call_tool(tc.name, tc.arguments)
                    except Exception as exc:
                        logger.warning("工具 %s 调用失败: %s", tc.name, exc)
                        tool_result = f"工具执行出错：{exc}"  # 把错误喂回模型，让它有机会调整策略

                used_sources.append(f"{tc.name}({tc.arguments})")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": tool_result,
                })
        else:
            # for-else：循环跑满 MAX_TOOL_ITERATIONS 都没 break，说明模型没能在限定轮数内收敛
            logger.warning("会话 %s 达到最大工具调用轮数仍未得出结论", session_id)
            answer = "这个问题需要的排查步骤比较多，我暂时没能在限定轮数内给出完整结论，建议换个更具体的问法，或转人工处理。"

        await self._memory.add_message(session_id, "user", question)
        await self._memory.add_message(session_id, "assistant", answer)

        return ChatResponse(message=answer, session_id=session_id, sources=used_sources,
                            elapsed_ms=int((time.time() - start) * 1000),
                            history_len=len(history) + 2,  # 包含当前问答
                            tools_used=["RAG", "Memory", "LLM"])

    async def ask_stream(self, session_id: str, question: str) -> AsyncGenerator[dict[str, Any], None]:
        """流式版本的 Agent 问答。yield 出来的每个 dict 对应一个 SSE 事件：
        - {"event": "tool_call", "name": ..., "arguments": ...}       工具开始调用
        - {"event": "tool_result", "name": ..., "result": ...}         工具返回结果
        - {"event": "answer_chunk", "content": ...}                     最终答案的文本片段
        - {"event": "done", "sources": [...]}                            结束标志
        - {"event": "error", "message": ...}                             出错
        """
        if self._mcp is None:
            async for chunk in self._ask_stream_no_tools(session_id, question):
                yield chunk
            return

        try:
            tools_schema = mcp_tools_to_openai_schema(await self._mcp.list_tools())
        except Exception as exc:
            yield {"event": "error", "message": f"获取工具列表失败: {exc}"}
            return

        history = await self._memory.get_history(session_id)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *history,
            {"role": "user", "content": question},
        ]

        full_answer = ""
        used_sources: list[str] = []
        seen_calls: set[str] = set()

        for step in range(MAX_TOOL_ITERATIONS):
            step_content = ""
            pending_tool_calls = None

            async for chunk in self._llm.chat_stream(messages, tools=tools_schema):
                if chunk.type == "content" and chunk.content:
                    step_content += chunk.content
                    full_answer += chunk.content
                    yield {"event": "answer_chunk", "content": chunk.content}
                elif chunk.type == "tool_calls":
                    pending_tool_calls = chunk.tool_calls
                elif chunk.type == "done":
                    pass  # 循环外统一处理结束

            if pending_tool_calls is None:
                # 这一轮没有工具调用意图，说明模型已经给出最终答案，流程结束
                break

            # 把本轮的调用意图加入历史
            messages.append({
                "role": "assistant",
                "content": step_content or None,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.name, "arguments": json.dumps(tc.arguments, ensure_ascii=False)},
                    }
                    for tc in pending_tool_calls
                ],
            })

            for tc in pending_tool_calls:
                yield {"event": "tool_call", "name": tc.name, "arguments": tc.arguments}

                call_signature = f"{tc.name}:{json.dumps(tc.arguments, sort_keys=True)}"
                if call_signature in seen_calls:
                    tool_result = "该工具已用相同参数调用过，请基于已有结果直接回答，不要重复调用。"
                else:
                    seen_calls.add(call_signature)
                    try:
                        tool_result = await self._mcp.call_tool(tc.name, tc.arguments)
                    except Exception as exc:
                        logger.warning("工具 %s 调用失败: %s", tc.name, exc)
                        tool_result = f"工具执行出错：{exc}"

                used_sources.append(f"{tc.name}({tc.arguments})")
                yield {"event": "tool_result", "name": tc.name, "result": tool_result}

                messages.append({"role": "tool", "tool_call_id": tc.id, "content": tool_result})
        else:
            fallback = "这个问题需要的排查步骤比较多，我暂时没能在限定轮数内给出完整结论，建议换个更具体的问法。"
            full_answer = fallback
            yield {"event": "answer_chunk", "content": fallback}

        await self._memory.add_message(session_id, "user", question)
        await self._memory.add_message(session_id, "assistant", full_answer)

        yield {"event": "done", "sources": used_sources}

    async def _ask_stream_no_tools(self, session_id: str, question: str) -> AsyncGenerator[dict[str, Any], None]:
        """没有配置MCP时的降级流式问答（纯RAG，不涉及工具调用）。"""
        retrieved = await self._rag.retrieve(question, top_k=3)
        context = "\n".join(f"- {r['text']}" for r in retrieved) or "（知识库未检索到相关内容）"
        history = await self._memory.get_history(session_id)
        messages = [
            {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n相关知识：\n{context}"},
            *history,
            {"role": "user", "content": question},
        ]

        full_answer = ""
        async for chunk in self._llm.chat_stream(messages):
            if chunk.type == "content" and chunk.content:
                full_answer += chunk.content
                yield {"event": "answer_chunk", "content": chunk.content}

        await self._memory.add_message(session_id, "user", question)
        await self._memory.add_message(session_id, "assistant", full_answer)
        yield {"event": "done", "sources": [r["text"][:50] for r in retrieved]}

    async def ask(self, session_id: str, question: str) -> ChatResponse:
        start = time.time()
        # 1. 检索知识库
        retrieved = await self._rag.retrieve(question, top_k=3)
        context = "\n".join(f"- {r['text']}" for r in retrieved) or "（知识库未检索到相关内容）"

        # 2. 取历史对话
        history = await self._memory.get_history(session_id)

        # 3. 组装消息
        messages = [
            {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n相关知识：\n{context}"},
            *history,
            {"role": "user", "content": question},
        ]

        # 4. 调用LLM
        response = await self._llm.chat(messages)
        answer = response.content or "抱歉，我暂时无法回答这个问题。"

        # 5. 更新记忆
        await self._memory.add_message(session_id, "user", question)
        await self._memory.add_message(session_id, "assistant", answer)

        return ChatResponse(
            message=answer,
            session_id=session_id,
            sources=[r["text"][:50] for r in retrieved],
            elapsed_ms=int((time.time() - start) * 1000),
            history_len=len(history) + 2,  # 包含当前问答
            tools_used=["RAG", "Memory", "LLM"]
        )

    async def get_session_history(self, session_id: str):
        """获取会话历史"""
        history = await self._memory.get_history(session_id)
        return {
            "session_id": session_id,
            "history": history,
            "history_len": len(history),
        }

    async def list_sessions(self):
        """列出所有会话ID"""
        sessions = await self._memory.list_sessions()
        return {
            "sessions": sessions,
            "total": len(sessions),
        }

    async def delete_session(self, session_id: str):
        """删除会话历史"""
        await self._memory.delete_session(session_id)
        return {
            "session_id": session_id,
            "status": "deleted",
        }
