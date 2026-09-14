# app/infrastructure/llm/deepseek_client.py
import json
import logging

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.exceptions import UpstreamServiceError
from app.infrastructure.llm.base import LLMClient, LLMResponse, ToolCall, StreamChunk

from collections.abc import AsyncGenerator

logger = logging.getLogger(__name__)


class DeepSeekClient(LLMClient):
    def __init__(self):
        self._client = AsyncOpenAI(api_key=settings.DEEPSEEK_API_KEY, base_url=settings.DEEPSEEK_BASE_URL)
        self._model = settings.DEEPSEEK_MODEL

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    async def chat(
            self, messages: list[dict], tools: list[dict] | None = None, temperature: float = 0.0
    ) -> LLMResponse:
        kwargs = {"model": self._model, "messages": messages, "temperature": temperature}
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"  # 让模型自己判断要不要调用

        try:
            resp = await self._client.chat.completions.create(**kwargs)
        except Exception as exc:
            logger.error("DeepSeek 调用失败: %s", exc)
            raise UpstreamServiceError("DeepSeek", str(exc)) from exc

        message = resp.choices[0].message
        tool_calls = [
            ToolCall(id=tc.id, name=tc.function.name, arguments=json.loads(tc.function.arguments))
            for tc in (message.tool_calls or [])
        ]
        return LLMResponse(content=message.content, tool_calls=tool_calls)

    async def chat_stream(
            self, messages: list[dict], tools: list[dict] | None = None, temperature: float = 0.0
    ) -> AsyncGenerator[StreamChunk, None]:
        kwargs = {"model": self._model, "messages": messages, "temperature": temperature, "stream": True}
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        try:
            stream = await self._client.chat.completions.create(**kwargs)
        except Exception as exc:
            logger.error("DeepSeek 流式调用失败: %s", exc)
            raise UpstreamServiceError("DeepSeek", str(exc)) from exc

        # 工具调用的参数是分片到达的，按 index 累积拼接，最后统一解析
        tool_call_buffers: dict[int, dict] = {}

        async for event in stream:
            delta = event.choices[0].delta
            finish_reason = event.choices[0].finish_reason

            if delta.content:
                yield StreamChunk(type="content", content=delta.content)

            if delta.tool_calls:
                for tc_delta in delta.tool_calls:
                    idx = tc_delta.index
                    if idx not in tool_call_buffers:
                        tool_call_buffers[idx] = {"id": "", "name": "", "arguments": ""}
                    if tc_delta.id:
                        tool_call_buffers[idx]["id"] = tc_delta.id
                    if tc_delta.function and tc_delta.function.name:
                        tool_call_buffers[idx]["name"] = tc_delta.function.name
                    if tc_delta.function and tc_delta.function.arguments:
                        tool_call_buffers[idx]["arguments"] += tc_delta.function.arguments

            if finish_reason == "tool_calls":
                tool_calls = [
                    ToolCall(id=buf["id"], name=buf["name"], arguments=json.loads(buf["arguments"] or "{}"))
                    for buf in tool_call_buffers.values()
                ]
                yield StreamChunk(type="tool_calls", tool_calls=tool_calls)
                return

            if finish_reason == "stop":
                yield StreamChunk(type="done")
                return
