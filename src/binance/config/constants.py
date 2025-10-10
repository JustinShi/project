"""系统常量定义"""

from enum import Enum


class OrderStatus(str, Enum):
    """订单状态"""

    PENDING = "PENDING"  # 待提交
    SUBMITTED = "SUBMITTED"  # 已提交
    PARTIALLY_FILLED = "PARTIALLY_FILLED"  # 部分成交
    FILLED = "FILLED"  # 完全成交
    CANCELLING = "CANCELLING"  # 取消中
    CANCELLED = "CANCELLED"  # 已取消
    FAILED = "FAILED"  # 失败
    EXPIRED = "EXPIRED"  # 已过期


class OrderSide(str, Enum):
    """订单方向"""

    BUY = "BUY"  # 买入
    SELL = "SELL"  # 卖出


class OrderType(str, Enum):
    """订单类型"""

    LIMIT = "LIMIT"  # 限价单
    MARKET = "MARKET"  # 市价单
    OTO = "OTO"  # One-Triggers-the-Other


class OTOOrderPairStatus(str, Enum):
    """OTO订单对状态"""

    PENDING = "PENDING"  # 待提交
    BUY_FILLED = "BUY_FILLED"  # 买单已成交
    COMPLETED = "COMPLETED"  # 完全完成
    CANCELLED = "CANCELLED"  # 已取消
    FAILED = "FAILED"  # 失败


class PriceOffsetMode(str, Enum):
    """价格偏移模式"""

    PERCENTAGE = "PERCENTAGE"  # 百分比偏移（仅支持此模式）


class TradingStatus(str, Enum):
    """交易状态"""

    ACTIVE = "ACTIVE"  # 活跃（正在交易）
    PAUSED = "PAUSED"  # 暂停
    STOPPED = "STOPPED"  # 停止
    ERROR = "ERROR"  # 错误状态


class PauseReason(str, Enum):
    """暂停原因"""

    MANUAL = "MANUAL"  # 手动暂停
    INSUFFICIENT_BALANCE = "INSUFFICIENT_BALANCE"  # 余额不足
    WS_DISCONNECTED = "WS_DISCONNECTED"  # WebSocket连接中断
    PRICE_VOLATILITY = "PRICE_VOLATILITY"  # 价格剧烈波动
    ORDER_TIMEOUT = "ORDER_TIMEOUT"  # 订单超时
    API_ERROR = "API_ERROR"  # API错误
    RATE_LIMITED = "RATE_LIMITED"  # 触发限流


class CacheKeyPrefix(str, Enum):
    """Redis缓存键前缀"""

    TOKEN_PRECISION = "token:precision:"  # 代币精度
    TOKEN_MAPPING = "token:mapping:"  # 代币符号映射
    PRICE_HISTORY = "price:history:"  # 价格历史
    USER_RATE_LIMIT = "rate:limit:user:"  # 用户请求限流


# 缓存过期时间（秒）
CACHE_TTL_TOKEN_INFO = 86400  # 代币信息缓存24小时
CACHE_TTL_PRICE = 60  # 价格数据缓存60秒

# API请求超时（秒）
API_TIMEOUT_DEFAULT = 30  # 默认超时
API_TIMEOUT_WEBSOCKET = 10  # WebSocket超时

# 重试配置
MAX_RETRY_ATTEMPTS = 3  # 最大重试次数
RETRY_DELAY_BASE = 1  # 重试基础延迟（秒）

# WebSocket URL
BINANCE_WS_BASE_URL = "wss://nbstream.binance.com/lvt-p"

# HTTP API基础URL
BINANCE_API_BASE_URL = "https://www.binance.com"

