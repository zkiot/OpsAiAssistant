"""认证/鉴权占位模块。

真实项目按需实现，比如：
- API Key 校验（内部服务间调用）
- JWT 校验 + FastAPI 的 Depends(get_current_user)
- OAuth2（如果要接第三方登录）

示例（按需取消注释并实现）：

from fastapi import Header, HTTPException, status

async def verify_api_key(x_api_key: str = Header(...)) -> None:
    if x_api_key != settings.INTERNAL_API_KEY:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "无效的API Key")
"""
