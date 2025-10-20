#!/usr/bin/env python3
"""简化版空投积分查询 - 只输出用户ID、姓名、总积分和日期"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any


# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select

from src.binance.infrastructure.binance_client.http_client import BinanceClient
from src.binance.infrastructure.database.models import User
from src.binance.infrastructure.database.session import get_db


# 禁用所有日志输出
logging.disable(logging.CRITICAL)


def clean_headers(headers: dict[str, Any]) -> dict[str, str]:
    """清理headers字典中的所有值"""
    import re

    cleaned_headers = {}

    for key, value in headers.items():
        if isinstance(value, str):
            # 移除所有控制字符（包括\r, \n, \t等）
            cleaned_value = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", value)
            # 移除多余的空格
            cleaned_value = cleaned_value.strip()
            # 移除连续的空白字符
            cleaned_value = re.sub(r"\s+", " ", cleaned_value)
            # 确保key也是字符串
            cleaned_key = str(key).strip()
            cleaned_headers[cleaned_key] = cleaned_value
        else:
            # 非字符串值转换为字符串并清理
            cleaned_value = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", str(value))
            cleaned_value = cleaned_value.strip()
            cleaned_value = re.sub(r"\s+", " ", cleaned_value)
            cleaned_key = str(key).strip()
            cleaned_headers[cleaned_key] = cleaned_value

    return cleaned_headers


async def get_user_airdrop_score(user_id: int, client: BinanceClient) -> dict | None:
    """查询单个用户的空投积分"""
    try:
        score_data = await client.get_user_airdrop_score()
        return score_data
    except Exception:
        return None


async def query_simple_airdrop_scores():
    """查询所有用户的空投积分（简化版）"""
    print("用户ID\t姓名\t总积分\t查询日期")
    print("-" * 50)

    async for session in get_db():
        # 获取所有用户
        result = await session.execute(select(User))
        users = result.scalars().all()

        if not users:
            print("未找到任何用户")
            return

        # 并发查询所有用户的空投积分
        tasks = []
        for user in users:
            if user.headers:
                try:
                    # 解析headers字符串为字典
                    headers = (
                        json.loads(user.headers)
                        if isinstance(user.headers, str)
                        else user.headers
                    )

                    # 清理headers中的非法字符
                    cleaned_headers = clean_headers(headers)

                    # 创建BinanceClient实例
                    client = BinanceClient(cleaned_headers, None)
                    task = get_user_airdrop_score(user.id, client)
                    tasks.append((user.id, user.name, task))
                except Exception:
                    # 如果解析失败，添加None任务
                    tasks.append((user.id, user.name, None))
            else:
                # 如果没有headers，添加None任务
                tasks.append((user.id, user.name, None))

        # 等待所有查询完成
        for user_id, user_name, task in tasks:
            if task is None:
                print(
                    f"{user_id}\t{user_name or 'N/A'}\tN/A\t{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
            else:
                try:
                    score_data = await task
                    if score_data:
                        total_score = score_data.get("sumScore", "0")
                        print(
                            f"{user_id}\t{user_name or 'N/A'}\t{total_score}\t{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        )
                    else:
                        print(
                            f"{user_id}\t{user_name or 'N/A'}\t查询失败\t{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        )
                except Exception:
                    print(
                        f"{user_id}\t{user_name or 'N/A'}\t查询失败\t{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    )

        break


if __name__ == "__main__":
    asyncio.run(query_simple_airdrop_scores())
