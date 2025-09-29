"""
时间处理工具
提供常用的时间操作和格式化功能
"""

import time
from datetime import date, datetime, timedelta
from typing import ClassVar, Dict, Optional, Union

from loguru import logger


class TimeUtil:
    """时间工具类"""

    # 常用时间格式
    FORMATS: ClassVar[Dict[str, str]] = {
        "datetime": "%Y-%m-%d %H:%M:%S",
        "date": "%Y-%m-%d",
        "time": "%H:%M:%S",
        "iso": "%Y-%m-%dT%H:%M:%S",
        "timestamp": "%Y%m%d%H%M%S",
        "filename": "%Y%m%d_%H%M%S",
    }

    @staticmethod
    def now() -> datetime:
        """获取当前时间"""
        return datetime.now()

    @staticmethod
    def today() -> date:
        """获取今天日期"""
        return date.today()

    @staticmethod
    def timestamp() -> float:
        """获取当前时间戳"""
        return time.time()

    @staticmethod
    def format_datetime(dt: Union[datetime, date], fmt: str = "datetime") -> str:
        """格式化时间"""
        if isinstance(dt, date) and not isinstance(dt, datetime):
            dt = datetime.combine(dt, datetime.min.time())

        if fmt in TimeUtil.FORMATS:
            fmt = TimeUtil.FORMATS[fmt]

        return dt.strftime(fmt)

    @staticmethod
    def parse_datetime(time_str: str, fmt: str = "datetime") -> datetime:
        """
        解析时间字符串

        Args:
            time_str: 时间字符串
            fmt: 时间格式

        Returns:
            解析后的时间对象
        """
        if fmt in TimeUtil.FORMATS:
            fmt = TimeUtil.FORMATS[fmt]

        return datetime.strptime(time_str, fmt)

    @staticmethod
    def safe_parse_datetime(
        time_str: str, fmt: str = "datetime", default: Optional[datetime] = None
    ) -> Optional[datetime]:
        """
        安全的时间解析, 失败时返回默认值

        Args:
            time_str: 时间字符串
            fmt: 时间格式
            default: 默认值

        Returns:
            解析后的时间对象或默认值
        """
        try:
            return TimeUtil.parse_datetime(time_str, fmt)
        except (ValueError, TypeError) as e:
            logger.warning(f"时间解析失败: {time_str}, 格式: {fmt}, 错误: {e}")
            return default

    @staticmethod
    def add_days(dt: Union[datetime, date], days: int) -> Union[datetime, date]:
        """添加天数"""
        if isinstance(dt, date) and not isinstance(dt, datetime):
            return dt + timedelta(days=days)
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
    def diff_days(dt1: Union[datetime, date], dt2: Union[datetime, date]) -> int:
        """计算两个日期之间的天数差"""
        if isinstance(dt1, datetime):
            dt1 = dt1.date()
        if isinstance(dt2, datetime):
            dt2 = dt2.date()
        return (dt1 - dt2).days

    @staticmethod
    def diff_seconds(dt1: datetime, dt2: datetime) -> float:
        """计算两个时间之间的秒数差"""
        return (dt1 - dt2).total_seconds()

    @staticmethod
    def diff_minutes(dt1: datetime, dt2: datetime) -> float:
        """计算两个时间之间的分钟数差"""
        return TimeUtil.diff_seconds(dt1, dt2) / 60

    @staticmethod
    def diff_hours(dt1: datetime, dt2: datetime) -> float:
        """计算两个时间之间的小时数差"""
        return TimeUtil.diff_seconds(dt1, dt2) / 3600

    @staticmethod
    def is_same_day(dt1: Union[datetime, date], dt2: Union[datetime, date]) -> bool:
        """判断是否为同一天"""
        if isinstance(dt1, datetime):
            dt1 = dt1.date()
        if isinstance(dt2, datetime):
            dt2 = dt2.date()
        return dt1 == dt2

    @staticmethod
    def is_weekend(dt: Union[datetime, date]) -> bool:
        """判断是否为周末"""
        if isinstance(dt, datetime):
            dt = dt.date()
        return dt.weekday() >= 5

    @staticmethod
    def is_weekday(dt: Union[datetime, date]) -> bool:
        """判断是否为工作日"""
        return not TimeUtil.is_weekend(dt)

    @staticmethod
    def start_of_day(dt: Union[datetime, date]) -> datetime:
        """获取一天的开始时间"""
        if isinstance(dt, date) and not isinstance(dt, datetime):
            dt = datetime.combine(dt, datetime.min.time())
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def end_of_day(dt: Union[datetime, date]) -> datetime:
        """获取一天的结束时间"""
        if isinstance(dt, date) and not isinstance(dt, datetime):
            dt = datetime.combine(dt, datetime.min.time())
        return dt.replace(hour=23, minute=59, second=59, microsecond=999999)

    @staticmethod
    def start_of_week(dt: Union[datetime, date]) -> datetime:
        """获取一周的开始时间(周一)"""
        if isinstance(dt, date) and not isinstance(dt, datetime):
            dt = datetime.combine(dt, datetime.min.time())

        days_since_monday = dt.weekday()
        return TimeUtil.start_of_day(dt - timedelta(days=days_since_monday))

    @staticmethod
    def end_of_week(dt: Union[datetime, date]) -> datetime:
        """获取一周的结束时间(周日)"""
        if isinstance(dt, date) and not isinstance(dt, datetime):
            dt = datetime.combine(dt, datetime.min.time())

        days_until_sunday = 6 - dt.weekday()
        return TimeUtil.end_of_day(dt + timedelta(days=days_until_sunday))

    @staticmethod
    def start_of_month(dt: Union[datetime, date]) -> datetime:
        """获取一个月的开始时间"""
        if isinstance(dt, date) and not isinstance(dt, datetime):
            dt = datetime.combine(dt, datetime.min.time())

        return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def end_of_month(dt: Union[datetime, date]) -> datetime:
        """获取一个月的结束时间"""
        if isinstance(dt, date) and not isinstance(dt, datetime):
            dt = datetime.combine(dt, datetime.min.time())

        # 获取下个月的第一天, 然后减去一天
        if dt.month == 12:
            next_month = dt.replace(year=dt.year + 1, month=1, day=1)
        else:
            next_month = dt.replace(month=dt.month + 1, day=1)

        return TimeUtil.end_of_day(next_month - timedelta(days=1))

    @staticmethod
    def format_duration(seconds: float) -> str:
        """格式化持续时间"""
        if seconds < 60:
            return f"{seconds:.1f}秒"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}分{remaining_seconds:.1f}秒"
        elif seconds < 86400:
            hours = int(seconds // 3600)
            remaining_minutes = int((seconds % 3600) // 60)
            return f"{hours}小时{remaining_minutes}分钟"
        else:
            days = int(seconds // 86400)
            remaining_hours = int((seconds % 86400) // 3600)
            return f"{days}天{remaining_hours}小时"

    @staticmethod
    def get_timezone_info() -> dict:
        """获取时区信息"""
        now = datetime.now()
        return {
            "utc_offset": now.utcoffset(),
            "tzname": now.tzname(),
            "dst": now.dst(),
        }

    @staticmethod
    def to_timestamp(dt: Union[datetime, date]) -> float:
        """转换为时间戳"""
        if isinstance(dt, date) and not isinstance(dt, datetime):
            dt = datetime.combine(dt, datetime.min.time())
        return dt.timestamp()

    @staticmethod
    def from_timestamp(timestamp: float) -> datetime:
        """从时间戳创建时间对象"""
        return datetime.fromtimestamp(timestamp)

    @staticmethod
    def get_age(
        birth_date: Union[datetime, date],
        reference_date: Optional[Union[datetime, date]] = None,
    ) -> int:
        """
        计算年龄

        Args:
            birth_date: 出生日期
            reference_date: 参考日期, 默认为今天

        Returns:
            年龄
        """
        if reference_date is None:
            reference_date = date.today()

        if isinstance(birth_date, datetime):
            birth_date = birth_date.date()
        if isinstance(reference_date, datetime):
            reference_date = reference_date.date()

        age = reference_date.year - birth_date.year
        if (reference_date.month, reference_date.day) < (
            birth_date.month,
            birth_date.day,
        ):
            age -= 1

        return age

    @staticmethod
    def is_leap_year(year: int) -> bool:
        """判断是否为闰年"""
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

    @staticmethod
    def get_days_in_month(year: int, month: int) -> int:
        """获取某月的天数"""
        if month == 2:
            return 29 if TimeUtil.is_leap_year(year) else 28
        elif month in [4, 6, 9, 11]:
            return 30
        else:
            return 31
