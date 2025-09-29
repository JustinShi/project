"""
重试/异常处理工具
提供统一的重试机制和异常处理
"""

import asyncio
import time
from functools import wraps
from typing import Any, Callable, Optional, Type

from loguru import logger


class RetryUtil:
    """重试工具类"""

    @staticmethod
    def _handle_retry_callback(
        on_retry: Optional[Callable], attempt: int, exception: Exception, delay: float
    ) -> None:
        """处理重试回调函数"""
        if on_retry:
            try:
                on_retry(attempt, exception, delay)
            except Exception as callback_error:
                logger.warning(f"重试回调函数执行失败: {callback_error}")

    @staticmethod
    def _execute_retry_attempt(
        func: Callable,
        args: tuple,
        kwargs: dict,
        exceptions: tuple,
        on_retry: Optional[Callable],
        attempt: int,
    ) -> Any:
        """执行重试尝试"""
        try:
            return func(*args, **kwargs)
        except exceptions as e:
            if on_retry:
                RetryUtil._handle_retry_callback(on_retry, attempt, e, 0)
            raise

    @staticmethod
    def retry(
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff_factor: float = 2.0,
        exceptions: tuple = (Exception,),
        on_retry: Optional[Callable] = None,
    ):
        """
        重试装饰器

        Args:
            max_attempts: 最大尝试次数
            delay: 初始延迟时间（秒）
            backoff_factor: 退避因子
            exceptions: 需要重试的异常类型
            on_retry: 重试回调函数

        Returns:
            装饰器函数
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                last_exception = None
                current_delay = delay

                for attempt in range(1, max_attempts + 1):
                    try:
                        return RetryUtil._execute_retry_attempt(
                            func, args, kwargs, exceptions, on_retry, attempt
                        )
                    except exceptions as e:
                        last_exception = e
                        if attempt < max_attempts:
                            logger.warning(f"重试 {attempt}/{max_attempts}: {e}")
                            time.sleep(current_delay)
                            current_delay *= backoff_factor
                        else:
                            logger.error(f"重试失败，已达到最大尝试次数: {e}")

                raise last_exception

            return wrapper

        return decorator

    @staticmethod
    def async_retry(
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff_factor: float = 2.0,
        exceptions: tuple = (Exception,),
        on_retry: Optional[Callable] = None,
    ):
        """
        异步重试装饰器

        Args:
            max_attempts: 最大尝试次数
            delay: 初始延迟时间（秒）
            backoff_factor: 退避因子
            exceptions: 需要重试的异常类型
            on_retry: 重试回调函数

        Returns:
            装饰器函数
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                last_exception = None
                current_delay = delay

                for attempt in range(1, max_attempts + 1):
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        if attempt < max_attempts:
                            logger.warning(f"异步重试 {attempt}/{max_attempts}: {e}")
                            if on_retry:
                                RetryUtil._handle_retry_callback(
                                    on_retry, attempt, e, current_delay
                                )
                            await asyncio.sleep(current_delay)
                            current_delay *= backoff_factor
                        else:
                            logger.error(f"异步重试失败，已达到最大尝试次数: {e}")

                raise last_exception

            return wrapper

        return decorator

    @staticmethod
    def retry_with_custom_strategy(
        strategy: Callable[[int, Exception], float],
        max_attempts: int = 3,
        exceptions: tuple = (Exception,),
    ):
        """
        自定义重试策略装饰器

        Args:
            strategy: 自定义延迟策略函数，接收尝试次数和异常，返回延迟时间
            max_attempts: 最大尝试次数
            exceptions: 需要重试的异常类型
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                last_exception = None

                for attempt in range(1, max_attempts + 1):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        if attempt < max_attempts:
                            delay = strategy(attempt, e)
                            logger.warning(
                                f"重试 {attempt}/{max_attempts}: {e}, 延迟 {delay} 秒"
                            )
                            time.sleep(delay)
                        else:
                            logger.error(f"重试失败，已达到最大尝试次数: {e}")

                raise last_exception

            return wrapper

        return decorator

    @staticmethod
    def exponential_backoff(attempt: int, exception: Exception) -> float:
        """指数退避策略"""
        return min(2**attempt, 60)  # 最大延迟60秒

    @staticmethod
    def linear_backoff(attempt: int, exception: Exception) -> float:
        """线性退避策略"""
        return attempt * 1.0

    @staticmethod
    def constant_delay(attempt: int, exception: Exception) -> float:
        """固定延迟策略"""
        return 1.0

    @staticmethod
    def jitter_backoff(attempt: int, exception: Exception) -> float:
        """带抖动的指数退避策略"""
        import random

        base_delay = min(2**attempt, 60)
        jitter = random.uniform(0.1, 0.5) * base_delay
        return base_delay + jitter


class ExceptionHandler:
    """异常处理类"""

    @staticmethod
    def handle_exception(
        exception: Exception,
        handler: Optional[Callable] = None,
        default_return: Any = None,
        log_error: bool = True,
    ) -> Any:
        """
        处理异常

        Args:
            exception: 要处理的异常
            handler: 自定义异常处理函数
            default_return: 异常时的默认返回值
            log_error: 是否记录错误日志
        """
        if log_error:
            logger.error(f"异常处理: {exception}")

        if handler:
            try:
                return handler(exception)
            except Exception as handler_error:
                logger.error(f"异常处理函数执行失败: {handler_error}")
                return default_return

        return default_return

    @staticmethod
    def safe_execute(
        func: Callable,
        default_return: Any = None,
        exceptions: tuple = (Exception,),
        *args,
        **kwargs,
    ) -> Any:
        """
        安全执行函数

        Args:
            func: 要执行的函数
            default_return: 异常时的默认返回值
            exceptions: 需要捕获的异常类型
            *args, **kwargs: 函数参数
        """
        try:
            return func(*args, **kwargs)
        except exceptions as e:
            logger.error(f"函数执行失败: {func.__name__}, 异常: {e}")
            return default_return

    @staticmethod
    async def safe_async_execute(
        func: Callable,
        default_return: Any = None,
        exceptions: tuple = (Exception,),
        *args,
        **kwargs,
    ) -> Any:
        """
        安全执行异步函数

        Args:
            func: 要执行的异步函数
            default_return: 异常时的默认返回值
            exceptions: 需要捕获的异常类型
            *args, **kwargs: 函数参数
        """
        try:
            return await func(*args, **kwargs)
        except exceptions as e:
            logger.error(f"异步函数执行失败: {func.__name__}, 异常: {e}")
            return default_return


class CircuitBreaker:
    """熔断器类"""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception,
    ):
        """
        初始化熔断器

        Args:
            failure_threshold: 失败阈值
            recovery_timeout: 恢复超时时间
            expected_exception: 预期的异常类型
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        调用函数

        Args:
            func: 要调用的函数
            *args, **kwargs: 函数参数

        Returns:
            函数返回值

        Raises:
            Exception: 熔断器打开时抛出异常
        """
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("熔断器打开，拒绝调用")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception:
            self._on_failure()
            raise

    def _on_success(self):
        """成功回调"""
        self.failure_count = 0
        self.state = "CLOSED"

    def _on_failure(self):
        """失败回调"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"熔断器打开，失败次数: {self.failure_count}")

    def get_state(self) -> str:
        """获取熔断器状态"""
        return self.state

    def reset(self):
        """重置熔断器"""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"
        logger.info("熔断器已重置")
