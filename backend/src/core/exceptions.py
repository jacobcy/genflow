from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from schemas.common import ErrorDetail, ErrorResponse


class GenflowException(Exception):
    pass


class ObjectNotFound(GenflowException):
    pass


class APIException(Exception):
    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        target: str = None,
        source: str = None
    ):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.target = target
        self.source = source


# 认证异常
class AuthException(APIException):
    def __init__(
        self,
        error_code: str = "AUTH_001",
        message: str = "认证失败",
        target: str = "credentials",
        source: str = "auth"
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=error_code,
            message=message,
            target=target,
            source=source
        )


# 请求异常
class RequestException(APIException):
    def __init__(
        self,
        error_code: str = "REQ_001",
        message: str = "无效的请求",
        target: str = "request",
        source: str = "request"
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=error_code,
            message=message,
            target=target,
            source=source
        )


# 权限异常
class ForbiddenException(APIException):
    def __init__(
        self,
        error_code: str = "AUTH_004",
        message: str = "权限不足",
        target: str = "permission",
        source: str = "auth"
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code=error_code,
            message=message,
            target=target,
            source=source
        )


# 频率限制异常
class RateLimitException(APIException):
    def __init__(
        self,
        error_code: str = "REQ_004",
        message: str = "请求频率超限",
        target: str = "ratelimit",
        source: str = "request"
    ):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code=error_code,
            message=message,
            target=target,
            source=source
        )


# 资源异常
class ResourceException(APIException):
    def __init__(
        self,
        error_code: str = "RES_001",
        message: str = "资源不存在",
        target: str = "resource",
        source: str = "resource"
    ):
        status_map = {
            "RES_001": status.HTTP_404_NOT_FOUND,        # 资源不存在
            "RES_002": status.HTTP_409_CONFLICT,         # 资源冲突
            "RES_003": status.HTTP_403_FORBIDDEN         # 资源禁止访问
        }
        super().__init__(
            status_code=status_map.get(error_code, status.HTTP_400_BAD_REQUEST),
            error_code=error_code,
            message=message,
            target=target,
            source=source
        )


# AI服务异常
class AIServiceException(APIException):
    def __init__(
        self,
        error_code: str = "AI_001",
        message: str = "AI服务错误",
        target: str = "ai_service",
        source: str = "ai"
    ):
        status_map = {
            "AI_001": status.HTTP_502_BAD_GATEWAY,       # AI服务错误
            "AI_002": status.HTTP_504_GATEWAY_TIMEOUT,   # AI服务超时
            "AI_003": status.HTTP_502_BAD_GATEWAY,       # AI响应无效
            "AI_004": status.HTTP_422_UNPROCESSABLE_ENTITY  # 内容过滤
        }
        super().__init__(
            status_code=status_map.get(error_code, status.HTTP_500_INTERNAL_SERVER_ERROR),
            error_code=error_code,
            message=message,
            target=target,
            source=source
        )


def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器"""

    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
        error_detail = ErrorDetail(
            code=exc.error_code,
            message=exc.message,
            target=exc.target,
            source=exc.source
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(error=error_detail).model_dump()
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        error_detail = ErrorDetail(
            code="SYS_001",
            message="系统内部错误",
            source="system"
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(error=error_detail).model_dump()
        )
