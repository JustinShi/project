"""
HTTP适配器

封装HTTP请求的适配器。
"""

import aiohttp
import asyncio
from typing import Dict, Any, Optional, Union
from datetime import datetime

from ..config.proxy_config import ProxyConfig
from ..config.user_config import UserConfig


class HttpAdapter:
    """HTTP适配器"""
    
    def __init__(
        self,
        proxy_config: ProxyConfig,
        user_config: UserConfig,
        timeout: int = 30
    ):
        """初始化适配器"""
        self.proxy_config = proxy_config
        self.user_config = user_config
        self.timeout = timeout
        self._session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取HTTP会话"""
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
            
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            
            # 配置代理
            proxy = None
            if self.proxy_config.is_enabled():
                proxy = self.proxy_config.get_proxy_url()
            
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                proxy=proxy
            )
        
        return self._session
    
    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """发送GET请求"""
        session = await self._get_session()
        
        # 获取用户配置
        if user_id:
            user_data = self.user_config.get_user_by_id(user_id)
            if user_data:
                # 合并请求头
                if headers is None:
                    headers = {}
                headers.update(user_data.get("headers", {}))
        
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {
                        "success": False,
                        "message": f"HTTP {response.status}: {response.reason}",
                        "data": None
                    }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "data": None
            }
    
    async def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """发送POST请求"""
        session = await self._get_session()
        
        # 获取用户配置
        if user_id:
            user_data = self.user_config.get_user_by_id(user_id)
            if user_data:
                # 合并请求头
                if headers is None:
                    headers = {}
                headers.update(user_data.get("headers", {}))
        
        try:
            async with session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {
                        "success": False,
                        "message": f"HTTP {response.status}: {response.reason}",
                        "data": None
                    }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "data": None
            }
    
    async def put(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """发送PUT请求"""
        session = await self._get_session()
        
        # 获取用户配置
        if user_id:
            user_data = self.user_config.get_user_by_id(user_id)
            if user_data:
                # 合并请求头
                if headers is None:
                    headers = {}
                headers.update(user_data.get("headers", {}))
        
        try:
            async with session.put(url, json=data, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {
                        "success": False,
                        "message": f"HTTP {response.status}: {response.reason}",
                        "data": None
                    }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "data": None
            }
    
    async def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """发送DELETE请求"""
        session = await self._get_session()
        
        # 获取用户配置
        if user_id:
            user_data = self.user_config.get_user_by_id(user_id)
            if user_data:
                # 合并请求头
                if headers is None:
                    headers = {}
                headers.update(user_data.get("headers", {}))
        
        try:
            async with session.delete(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {
                        "success": False,
                        "message": f"HTTP {response.status}: {response.reason}",
                        "data": None
                    }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "data": None
            }
    
    async def close(self):
        """关闭HTTP会话"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
