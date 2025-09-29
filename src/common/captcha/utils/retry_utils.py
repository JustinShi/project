"""重试工具模块"""

import asyncio
import random
import time
from functools import wraps
from typing import Any, Callable, Dict, Optional


class RetryConfig:
    """重试配置类"""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
        retry_exceptions: tuple = (Exception,),
        stop_exceptions: tuple = (),
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.retry_exceptions = retry_exceptions
        self.stop_exceptions = stop_exceptions


def exponential_backoff(
    attempt: int,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
) -> float:
    """
    计算指数退避延迟时间

    Args:
        attempt: 当前尝试次数 (从 0 开始)
        base_delay: 基础延迟时间
        max_delay: 最大延迟时间
        backoff_factor: 退避因子
        jitter: 是否添加随机抖动

    Returns:
        float: 延迟时间（秒）
    """
    if attempt <= 0:
        return 0

    # 计算指数退避延迟
    delay = base_delay * (backoff_factor ** (attempt - 1))

    # 限制最大延迟
    delay = min(delay, max_delay)

    # 添加随机抖动
    if jitter:
        delay = delay * (0.5 + random.random() * 0.5)

    return delay


def retry_on_failure(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    retry_exceptions: tuple = (Exception,),
    stop_exceptions: tuple = (),
    on_retry: Optional[Callable] = None,
):
    """
    重试装饰器

    Args:
        max_retries: 最大重试次数
        base_delay: 基础延迟时间
        max_delay: 最大延迟时间
        backoff_factor: 退避因子
        jitter: 是否添加随机抖动
        retry_exceptions: 需要重试的异常类型
        stop_exceptions: 停止重试的异常类型
        on_retry: 重试时的回调函数
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except stop_exceptions as e:
                    # 遇到停止异常，直接抛出
                    raise e
                except retry_exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        # 最后一次尝试失败，抛出异常
                        raise e

                    # 计算延迟时间
                    delay = exponential_backoff(
                        attempt + 1, base_delay, max_delay, backoff_factor, jitter
                    )

                    # 调用重试回调
                    if on_retry:
                        try:
                            on_retry(attempt + 1, e, delay)
                        except Exception:
                            pass  # 忽略回调函数中的异常

                    # 等待延迟时间
                    if delay > 0:
                        await asyncio.sleep(delay)
                except Exception as e:
                    # 不在重试范围内的异常，直接抛出
                    raise e

            # 理论上不会到达这里
            raise last_exception

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except stop_exceptions as e:
                    # 遇到停止异常，直接抛出
                    raise e
                except retry_exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        # 最后一次尝试失败，抛出异常
                        raise e

                    # 计算延迟时间
                    delay = exponential_backoff(
                        attempt + 1, base_delay, max_delay, backoff_factor, jitter
                    )

                    # 调用重试回调
                    if on_retry:
                        try:
                            on_retry(attempt + 1, e, delay)
                        except Exception:
                            pass  # 忽略回调函数中的异常

                    # 等待延迟时间
                    if delay > 0:
                        time.sleep(delay)
                except Exception as e:
                    # 不在重试范围内的异常，直接抛出
                    raise e

            # 理论上不会到达这里
            raise last_exception

        # 根据函数类型返回对应的包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class RetryManager:
    """重试管理器"""

    def __init__(self, config: RetryConfig):
        self.config = config
        self.retry_count = 0
        self.last_exception = None

    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        执行函数并处理重试

        Args:
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数

        Returns:
            Any: 函数执行结果
        """
        self.retry_count = 0
        self.last_exception = None

        for attempt in range(self.config.max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except self.config.stop_exceptions as e:
                # 遇到停止异常，直接抛出
                raise e
            except self.config.retry_exceptions as e:
                self.last_exception = e
                self.retry_count = attempt + 1

                if attempt == self.config.max_retries:
                    # 最后一次尝试失败，抛出异常
                    raise e

                # 计算延迟时间
                delay = exponential_backoff(
                    attempt + 1,
                    self.config.base_delay,
                    self.config.max_delay,
                    self.config.backoff_factor,
                    self.config.jitter,
                )

                # 等待延迟时间
                if delay > 0:
                    await asyncio.sleep(delay)
            except Exception as e:
                # 不在重试范围内的异常，直接抛出
                raise e

        # 理论上不会到达这里
        raise self.last_exception

    def get_retry_info(self) -> Dict[str, Any]:
        """获取重试信息"""
        return {
            "retry_count": self.retry_count,
            "last_exception": str(self.last_exception) if self.last_exception else None,
            "config": {
                "max_retries": self.config.max_retries,
                "base_delay": self.config.base_delay,
                "max_delay": self.config.max_delay,
                "backoff_factor": self.config.backoff_factor,
                "jitter": self.config.jitter,
            },
        }


def create_retry_config(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    retry_exceptions: tuple = (Exception,),
    stop_exceptions: tuple = (),
) -> RetryConfig:
    """
    创建重试配置

    Args:
        max_retries: 最大重试次数
        base_delay: 基础延迟时间
        max_delay: 最大延迟时间
        backoff_factor: 退避因子
        jitter: 是否添加随机抖动
        retry_exceptions: 需要重试的异常类型
        stop_exceptions: 停止重试的异常类型

    Returns:
        RetryConfig: 重试配置对象
    """
    return RetryConfig(
        max_retries=max_retries,
        base_delay=base_delay,
        max_delay=max_delay,
        backoff_factor=backoff_factor,
        jitter=jitter,
        retry_exceptions=retry_exceptions,
        stop_exceptions=stop_exceptions,
    )


def retry_with_config(config: RetryConfig, on_retry: Optional[Callable] = None):
    """
    使用配置对象的重试装饰器

    Args:
        config: 重试配置对象
        on_retry: 重试时的回调函数
    """
    return retry_on_failure(
        max_retries=config.max_retries,
        base_delay=config.base_delay,
        max_delay=config.max_delay,
        backoff_factor=config.backoff_factor,
        jitter=config.jitter,
        retry_exceptions=config.retry_exceptions,
        stop_exceptions=config.stop_exceptions,
        on_retry=on_retry,
    )
