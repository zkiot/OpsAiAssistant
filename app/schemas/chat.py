from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="会话ID，用于关联多轮对话历史")
    message: str = Field(..., min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    message: str
    session_id: str
    sources: list[str] = Field(default_factory=list, description="引用的知识库来源")
    elapsed_ms: int = Field(..., description="处理请求的耗时，单位毫秒")
    history_len: int = Field(..., description="当前会话的历史消息条数")
    tools_used: list[str] = Field(default_factory=list, description="在生成回答过程中使用的工具列表")
