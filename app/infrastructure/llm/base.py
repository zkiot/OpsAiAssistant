# app/infrastructure/llm/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from collections.abc import AsyncGenerator
from typing import Literal


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict


@dataclass
class StreamChunk:
    type: Literal["content", "tool_calls", "done"]
    content: str | None = None
    tool_calls: list[ToolCall] | None = None


@dataclass
class LLMResponse:
    content: str | None
    tool_calls: list[ToolCall] = field(default_factory=list)

    @property
    def has_tool_calls(self) -> bool:
        return len(self.tool_calls) > 0


class LLMClient(ABC):
    @abstractmethod
    async def chat(
            self, messages: list[dict], tools: list[dict] | None = None, temperature: float = 0.0
    ) -> LLMResponse: ...

    @abstractmethod
    def chat_stream(
            self, messages: list[dict], tools: list[dict] | None = None, temperature: float = 0.0
    ) -> AsyncGenerator[StreamChunk, None]: ...
