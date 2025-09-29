"""
交易常量

交易相关的常量定义。
"""

from decimal import Decimal


class TradingConstants:
    """交易常量"""
    
    # 订单方向
    ORDER_SIDE_BUY = "BUY"
    ORDER_SIDE_SELL = "SELL"
    
    # 订单类型
    ORDER_TYPE_LIMIT = "LIMIT"
    ORDER_TYPE_MARKET = "MARKET"
    
    # 订单有效期
    TIME_IN_FORCE_GTC = "GTC"  # Good Till Cancel
    TIME_IN_FORCE_IOC = "IOC"  # Immediate or Cancel
    TIME_IN_FORCE_FOK = "FOK"  # Fill or Kill
    
    # 订单状态
    ORDER_STATUS_NEW = "NEW"
    ORDER_STATUS_PENDING = "PENDING"
    ORDER_STATUS_PARTIALLY_FILLED = "PARTIALLY_FILLED"
    ORDER_STATUS_FILLED = "FILLED"
    ORDER_STATUS_CANCELED = "CANCELED"
    ORDER_STATUS_REJECTED = "REJECTED"
    
    # 交易类型
    TRADE_TYPE_BUY = "BUY"
    TRADE_TYPE_SELL = "SELL"
    
    # 订单类型
    ORDER_TYPE_OTO = "OTO"  # One-Time Order
    ORDER_TYPE_NORMAL = "NORMAL"
    
    # 支付钱包类型
    PAYMENT_WALLET_TYPE_CARD = "CARD"
    PAYMENT_WALLET_TYPE_WALLET = "WALLET"
    PAYMENT_WALLET_TYPE_BANK = "BANK"
    
    # 链类型
    CHAIN_TYPE_BSC = "BSC"
    CHAIN_TYPE_ETH = "ETH"
    CHAIN_TYPE_POLYGON = "POLYGON"
    
    # 链ID
    CHAIN_ID_BSC = "56"
    CHAIN_ID_ETH = "1"
    CHAIN_ID_POLYGON = "137"
    
    # 默认精度
    DEFAULT_DECIMAL_PRECISION = 8
    DEFAULT_PRICE_PRECISION = 8
    DEFAULT_QUANTITY_PRECISION = 8
    
    # 最小数量
    MIN_QUANTITY = Decimal("0.00000001")
    MIN_PRICE = Decimal("0.00000001")
    
    # 最大数量
    MAX_QUANTITY = Decimal("1000000000")
    MAX_PRICE = Decimal("1000000000")
    
    # 手续费率
    DEFAULT_COMMISSION_RATE = Decimal("0.001")  # 0.1%
    
    # 风险控制
    DEFAULT_MAX_POSITION_SIZE = Decimal("0.1")  # 10%
    DEFAULT_MAX_DAILY_LOSS = Decimal("0.05")    # 5%
    DEFAULT_MAX_DAILY_VOLUME = Decimal("10000") # 10000 USDT
    DEFAULT_MIN_LIQUIDITY = Decimal("100000")   # 100000 USDT
    
    # 时间间隔
    DEFAULT_ORDER_TIMEOUT = 300  # 5分钟
    DEFAULT_TRADE_TIMEOUT = 60   # 1分钟
    
    # 重试配置
    DEFAULT_RETRY_COUNT = 3
    DEFAULT_RETRY_DELAY = 1.0
    DEFAULT_RETRY_BACKOFF = 2.0
    
    # 缓存配置
    DEFAULT_CACHE_TTL = 60  # 1分钟
    DEFAULT_ORDER_CACHE_TTL = 300  # 5分钟
    DEFAULT_WALLET_CACHE_TTL = 30  # 30秒
    
    # WebSocket配置
    DEFAULT_WS_PING_INTERVAL = 20
    DEFAULT_WS_PING_TIMEOUT = 10
    DEFAULT_WS_RECONNECT_DELAY = 5
    
    # 支持的交易对
    SUPPORTED_QUOTE_ASSETS = ["USDT", "USDC", "BUSD", "BNB", "BTC", "ETH"]
    
    # Alpha代币前缀
    ALPHA_TOKEN_PREFIX = "ALPHA_"
    
    # 默认用户配置
    DEFAULT_USER_ENABLED = True
    DEFAULT_USER_TIMEOUT = 30
    
    # 日志级别
    LOG_LEVEL_DEBUG = "DEBUG"
    LOG_LEVEL_INFO = "INFO"
    LOG_LEVEL_WARNING = "WARNING"
    LOG_LEVEL_ERROR = "ERROR"
    LOG_LEVEL_CRITICAL = "CRITICAL"
