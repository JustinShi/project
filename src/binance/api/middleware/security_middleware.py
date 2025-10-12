"""安全中间件"""

import time
from collections.abc import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from binance.application.services.security_service import (
    SecurityService,
)
from binance.infrastructure.logging.logger import get_logger


logger = get_logger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """安全中间件"""

    def __init__(self, app, security_service: SecurityService):
        super().__init__(app)
        self.security_service = security_service

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        start_time = time.time()

        # 获取用户ID（从请求头或查询参数）
        user_id = self._extract_user_id(request)

        # 获取端点
        endpoint = f"{request.method} {request.url.path}"

        # 检查频率限制
        if user_id:
            allowed, message = self.security_service.check_rate_limit(user_id, endpoint)
            if not allowed:
                logger.warning(
                    f"频率限制: 用户 {user_id} 访问 {endpoint} 被限制 - {message}"
                )
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Too Many Requests",
                        "message": message,
                        "retry_after": 60,
                    },
                )

        # 记录请求开始
        logger.info(f"请求开始: {request.method} {request.url.path} - 用户 {user_id}")

        try:
            # 处理请求
            response = await call_next(request)

            # 计算处理时间
            process_time = time.time() - start_time

            # 记录请求完成
            logger.info(
                f"请求完成: {request.method} {request.url.path} - "
                f"状态 {response.status_code} - 耗时 {process_time:.3f}s - 用户 {user_id}"
            )

            # 添加安全头
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

            # 记录审计日志
            if user_id:
                self.security_service.log_audit_event(
                    user_id=user_id,
                    action="api_request",
                    resource=endpoint,
                    details={
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": response.status_code,
                        "process_time": process_time,
                        "user_agent": request.headers.get("user-agent", ""),
                        "ip_address": request.client.host
                        if request.client
                        else "unknown",
                    },
                )

            return response

        except Exception as e:
            # 记录错误
            logger.error(
                f"请求异常: {request.method} {request.url.path} - {e!s} - 用户 {user_id}"
            )

            # 记录审计日志
            if user_id:
                self.security_service.log_audit_event(
                    user_id=user_id,
                    action="api_error",
                    resource=endpoint,
                    details={
                        "method": request.method,
                        "path": request.url.path,
                        "error": str(e),
                        "user_agent": request.headers.get("user-agent", ""),
                        "ip_address": request.client.host
                        if request.client
                        else "unknown",
                    },
                )

            # 返回通用错误响应
            return JSONResponse(
                status_code=500,
                content={"error": "Internal Server Error", "message": "服务器内部错误"},
            )

    def _extract_user_id(self, request: Request) -> int:
        """从请求中提取用户ID"""
        # 从查询参数获取
        user_id = request.query_params.get("user_id")
        if user_id:
            try:
                return int(user_id)
            except ValueError:
                pass

        # 从请求头获取
        user_id = request.headers.get("X-User-ID")
        if user_id:
            try:
                return int(user_id)
            except ValueError:
                pass

        # 从JWT令牌获取（如果有的话）
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            # 这里应该解析JWT令牌获取用户ID
            # 暂时返回默认值
            pass

        # 默认返回0（匿名用户）
        return 0


class RateLimitMiddleware(BaseHTTPMiddleware):
    """频率限制中间件"""

    def __init__(self, app, security_service: SecurityService):
        super().__init__(app)
        self.security_service = security_service

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        user_id = self._extract_user_id(request)
        endpoint = f"{request.method} {request.url.path}"

        # 检查频率限制
        allowed, message = self.security_service.check_rate_limit(user_id, endpoint)
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "message": message,
                    "retry_after": 60,
                },
            )

        return await call_next(request)

    def _extract_user_id(self, request: Request) -> int:
        """从请求中提取用户ID"""
        user_id = request.query_params.get("user_id")
        if user_id:
            try:
                return int(user_id)
            except ValueError:
                pass

        user_id = request.headers.get("X-User-ID")
        if user_id:
            try:
                return int(user_id)
            except ValueError:
                pass

        return 0


class AuditMiddleware(BaseHTTPMiddleware):
    """审计中间件"""

    def __init__(self, app, security_service: SecurityService):
        super().__init__(app)
        self.security_service = security_service

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        user_id = self._extract_user_id(request)
        endpoint = f"{request.method} {request.url.path}"

        # 记录请求开始
        self.security_service.log_audit_event(
            user_id=user_id,
            action="request_start",
            resource=endpoint,
            details={
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "user_agent": request.headers.get("user-agent", ""),
                "ip_address": request.client.host if request.client else "unknown",
            },
        )

        try:
            response = await call_next(request)

            # 记录请求完成
            self.security_service.log_audit_event(
                user_id=user_id,
                action="request_complete",
                resource=endpoint,
                details={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                },
            )

            return response

        except Exception as e:
            # 记录请求错误
            self.security_service.log_audit_event(
                user_id=user_id,
                action="request_error",
                resource=endpoint,
                details={
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                },
            )
            raise

    def _extract_user_id(self, request: Request) -> int:
        """从请求中提取用户ID"""
        user_id = request.query_params.get("user_id")
        if user_id:
            try:
                return int(user_id)
            except ValueError:
                pass

        user_id = request.headers.get("X-User-ID")
        if user_id:
            try:
                return int(user_id)
            except ValueError:
                pass

        return 0


class DataMaskingMiddleware(BaseHTTPMiddleware):
    """数据脱敏中间件"""

    def __init__(self, app, security_service: SecurityService):
        super().__init__(app)
        self.security_service = security_service

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        # 处理请求体脱敏
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
            if body:
                # 这里可以解析和脱敏请求体
                # 暂时跳过，因为需要根据具体的数据结构来处理
                pass

        response = await call_next(request)

        # 处理响应体脱敏
        if hasattr(response, "body"):
            # 这里可以脱敏响应体中的敏感数据
            # 暂时跳过，因为需要根据具体的数据结构来处理
            pass

        return response
