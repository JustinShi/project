"""
时间工具

时间相关的工具函数。
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, Union
import time


class TimeUtil:
    """时间工具类"""
    
    @staticmethod
    def now() -> datetime:
        """获取当前UTC时间"""
        return datetime.utcnow()
    
    @staticmethod
    def now_with_timezone() -> datetime:
        """获取当前带时区的时间"""
        return datetime.now(timezone.utc)
    
    @staticmethod
    def timestamp() -> float:
        """获取当前时间戳"""
        return time.time()
    
    @staticmethod
    def timestamp_ms() -> int:
        """获取当前毫秒时间戳"""
        return int(time.time() * 1000)
    
    @staticmethod
    def from_timestamp(timestamp: Union[int, float]) -> datetime:
        """从时间戳创建datetime"""
        if timestamp > 1e10:  # 毫秒时间戳
            timestamp = timestamp / 1000
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)
    
    @staticmethod
    def to_timestamp(dt: datetime) -> float:
        """将datetime转换为时间戳"""
        return dt.timestamp()
    
    @staticmethod
    def to_timestamp_ms(dt: datetime) -> int:
        """将datetime转换为毫秒时间戳"""
        return int(dt.timestamp() * 1000)
    
    @staticmethod
    def from_iso_string(iso_string: str) -> datetime:
        """从ISO字符串创建datetime"""
        return datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
    
    @staticmethod
    def to_iso_string(dt: datetime) -> str:
        """将datetime转换为ISO字符串"""
        return dt.isoformat()
    
    @staticmethod
    def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """格式化datetime"""
        return dt.strftime(format_str)
    
    @staticmethod
    def parse_datetime(date_string: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
        """解析datetime字符串"""
        return datetime.strptime(date_string, format_str)
    
    @staticmethod
    def add_days(dt: datetime, days: int) -> datetime:
        """添加天数"""
        return dt + timedelta(days=days)
    
    @staticmethod
    def add_hours(dt: datetime, hours: int) -> datetime:
        """添加小时"""
        return dt + timedelta(hours=hours)
    
    @staticmethod
    def add_minutes(dt: datetime, minutes: int) -> datetime:
        """添加分钟"""
        return dt + timedelta(minutes=minutes)
    
    @staticmethod
    def add_seconds(dt: datetime, seconds: int) -> datetime:
        """添加秒数"""
        return dt + timedelta(seconds=seconds)
    
    @staticmethod
    def start_of_day(dt: datetime) -> datetime:
        """获取一天的开始时间"""
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)
    
    @staticmethod
    def end_of_day(dt: datetime) -> datetime:
        """获取一天的结束时间"""
        return dt.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    @staticmethod
    def start_of_week(dt: datetime) -> datetime:
        """获取一周的开始时间"""
        days_since_monday = dt.weekday()
        return TimeUtil.start_of_day(dt - timedelta(days=days_since_monday))
    
    @staticmethod
    def start_of_month(dt: datetime) -> datetime:
        """获取一月的开始时间"""
        return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    @staticmethod
    def is_same_day(dt1: datetime, dt2: datetime) -> bool:
        """判断是否为同一天"""
        return dt1.date() == dt2.date()
    
    @staticmethod
    def is_same_week(dt1: datetime, dt2: datetime) -> bool:
        """判断是否为同一周"""
        return TimeUtil.start_of_week(dt1) == TimeUtil.start_of_week(dt2)
    
    @staticmethod
    def is_same_month(dt1: datetime, dt2: datetime) -> bool:
        """判断是否为同一月"""
        return dt1.year == dt2.year and dt1.month == dt2.month
    
    @staticmethod
    def days_between(dt1: datetime, dt2: datetime) -> int:
        """计算两个日期之间的天数"""
        return abs((dt2.date() - dt1.date()).days)
    
    @staticmethod
    def hours_between(dt1: datetime, dt2: datetime) -> float:
        """计算两个时间之间的小时数"""
        return abs((dt2 - dt1).total_seconds() / 3600)
    
    @staticmethod
    def minutes_between(dt1: datetime, dt2: datetime) -> float:
        """计算两个时间之间的分钟数"""
        return abs((dt2 - dt1).total_seconds() / 60)
    
    @staticmethod
    def seconds_between(dt1: datetime, dt2: datetime) -> float:
        """计算两个时间之间的秒数"""
        return abs((dt2 - dt1).total_seconds())
    
    @staticmethod
    def is_business_day(dt: datetime) -> bool:
        """判断是否为工作日"""
        return dt.weekday() < 5  # 0-4 为周一到周五
    
    @staticmethod
    def next_business_day(dt: datetime) -> datetime:
        """获取下一个工作日"""
        next_day = dt + timedelta(days=1)
        while not TimeUtil.is_business_day(next_day):
            next_day += timedelta(days=1)
        return next_day
    
    @staticmethod
    def previous_business_day(dt: datetime) -> datetime:
        """获取上一个工作日"""
        prev_day = dt - timedelta(days=1)
        while not TimeUtil.is_business_day(prev_day):
            prev_day -= timedelta(days=1)
        return prev_day
