"""
重试工具

重试相关的工具函数。
"""

import asyncio
import time
from typing import Callable, Any, Optional, Union
from functools import wraps


class RetryUtil:
    """重试工具类"""
    
    @staticmethod
    def retry(
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        exceptions: tuple = (Exception,),
        on_retry: Optional[Callable] = None
    ):
        """重试装饰器"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                last_exception = None
                current_delay = delay
                
                for attempt in range(max_attempts):
                    try:
                        if asyncio.iscoroutinefunction(func):
                            return await func(*args, **kwargs)
                        else:
                            return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        
                        if attempt < max_attempts - 1:
                            if on_retry:
                                on_retry(attempt + 1, e)
                            
                            await asyncio.sleep(current_delay)
                            current_delay *= backoff
                        else:
                            raise e
                
                raise last_exception
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs) -> Any:
                last_exception = None
                current_delay = delay
                
                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        
                        if attempt < max_attempts - 1:
                            if on_retry:
                                on_retry(attempt + 1, e)
                            
                            time.sleep(current_delay)
                            current_delay *= backoff
                        else:
                            raise e
                
                raise last_exception
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
    
    @staticmethod
    async def retry_async(
        func: Callable,
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        exceptions: tuple = (Exception,),
        on_retry: Optional[Callable] = None,
        *args,
        **kwargs
    ) -> Any:
        """异步重试函数"""
        last_exception = None
        current_delay = delay
        
        for attempt in range(max_attempts):
            try:
                return await func(*args, **kwargs)
            except exceptions as e:
                last_exception = e
                
                if attempt < max_attempts - 1:
                    if on_retry:
                        on_retry(attempt + 1, e)
                    
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
                else:
                    raise e
        
        raise last_exception
    
    @staticmethod
    def retry_sync(
        func: Callable,
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        exceptions: tuple = (Exception,),
        on_retry: Optional[Callable] = None,
        *args,
        **kwargs
    ) -> Any:
        """同步重试函数"""
        last_exception = None
        current_delay = delay
        
        for attempt in range(max_attempts):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                last_exception = e
                
                if attempt < max_attempts - 1:
                    if on_retry:
                        on_retry(attempt + 1, e)
                    
                    time.sleep(current_delay)
                    current_delay *= backoff
                else:
                    raise e
        
        raise last_exception
    
    @staticmethod
    def exponential_backoff(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
        """指数退避延迟"""
        delay = base_delay * (2 ** attempt)
        return min(delay, max_delay)
    
    @staticmethod
    def linear_backoff(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
        """线性退避延迟"""
        delay = base_delay * (attempt + 1)
        return min(delay, max_delay)
    
    @staticmethod
    def fixed_delay(attempt: int, delay: float = 1.0) -> float:
        """固定延迟"""
        return delay
    
    @staticmethod
    def jitter(delay: float, jitter_factor: float = 0.1) -> float:
        """添加抖动"""
        import random
        jitter = delay * jitter_factor * random.uniform(-1, 1)
        return max(0, delay + jitter)
