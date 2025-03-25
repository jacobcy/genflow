from uuid import uuid4
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RequestHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 生成请求ID
        if not request.headers.get("X-Request-ID"):
            request_id = f"req_{uuid4().hex[:6]}"
            # 不能直接修改request.headers，需要在内部状态中保存
            request.state.request_id = request_id
        else:
            request.state.request_id = request.headers.get("X-Request-ID")

        # 处理请求
        response = await call_next(request)

        # 向响应添加标准头
        response.headers["X-Request-ID"] = request.state.request_id

        return response
