from tenacity import retry, stop_after_attempt, wait_exponential

# 项目里对外部依赖（LLM、embedding、向量库）的调用统一用这个装饰器，
# 保持重试策略一致，避免每个 client 各写一套。
default_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
)
