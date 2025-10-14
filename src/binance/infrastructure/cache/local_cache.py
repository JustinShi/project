"""本地JSON缓存工具"""

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from binance.infrastructure.logging.logger import get_logger


logger = get_logger(__name__)

CACHE_DIR = Path("data/cache")
TOKEN_INFO_FILE = CACHE_DIR / "token_info.json"
TOKEN_PRECISION_FILE = CACHE_DIR / "token_precision.json"
CACHE_TTL_HOURS = 24


@dataclass
class CachedItem:
    data: dict[str, Any]
    cached_at: datetime

    @property
    def is_expired(self) -> bool:
        return datetime.now() - self.cached_at > timedelta(hours=CACHE_TTL_HOURS)


class LocalCache:
    """本地JSON文件缓存（使用单例模式确保缓存一致性）"""

    _instance: "LocalCache | None" = None

    def __new__(cls) -> "LocalCache":
        """单例模式：确保全局只有一个 LocalCache 实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized: bool = False
        return cls._instance

    def __init__(self) -> None:
        # 避免重复初始化
        if hasattr(self, "_initialized") and self._initialized:
            return

        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self._token_info: dict[str, CachedItem] = {}
        self._token_precision: dict[str, CachedItem] = {}
        self._load()
        self._initialized = True

    def _load(self) -> None:
        """加载文件内容到内存"""
        self._token_info = self._load_file(TOKEN_INFO_FILE)
        self._token_precision = self._load_file(TOKEN_PRECISION_FILE)

    def _load_file(self, path: Path) -> dict[str, CachedItem]:
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            result: dict[str, CachedItem] = {}
            for key, value in data.items():
                cached_at_text = value.get("cached_at")
                if not cached_at_text:
                    continue
                try:
                    cached_at = datetime.fromisoformat(cached_at_text)
                except ValueError:
                    logger.warning(
                        "local_cache_invalid_cached_at", file=str(path), entry=key
                    )
                    continue
                result[key.upper()] = CachedItem(
                    data=value.get("data", {}), cached_at=cached_at
                )
            return result
        except Exception as exc:
            logger.error("local_cache_load_error", file=str(path), error=str(exc))
            return {}

    def _save_file(self, path: Path, payload: dict[str, CachedItem]) -> None:
        try:
            serializable = {
                key: {
                    "data": value.data,
                    "cached_at": value.cached_at.isoformat(),
                }
                for key, value in payload.items()
            }
            path.write_text(
                json.dumps(serializable, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        except Exception as exc:
            logger.error("local_cache_save_error", file=str(path), error=str(exc))

    def get_token_info(self, symbol_short: str) -> dict[str, Any] | None:
        symbol = symbol_short.upper()
        item = self._token_info.get(symbol)
        if not item:
            return None
        if item.is_expired:
            logger.info("local_cache_token_info_expired", symbol=symbol)
            self._token_info.pop(symbol, None)
            self._save_file(TOKEN_INFO_FILE, self._token_info)
            return None
        return item.data

    def set_token_info(self, symbol_short: str, data: dict[str, Any]) -> None:
        symbol = symbol_short.upper()
        self._token_info[symbol] = CachedItem(data=data, cached_at=datetime.now())
        self._save_file(TOKEN_INFO_FILE, self._token_info)

    def set_all_token_info(self, items: dict[str, dict[str, Any]]) -> None:
        now = datetime.now()
        for symbol, data in items.items():
            symbol_upper = symbol.upper()
            self._token_info[symbol_upper] = CachedItem(data=data, cached_at=now)
        self._save_file(TOKEN_INFO_FILE, self._token_info)

    def get_token_precision(self, symbol_short: str) -> dict[str, Any] | None:
        symbol = symbol_short.upper()
        item = self._token_precision.get(symbol)
        if not item:
            return None
        if item.is_expired:
            logger.info("local_cache_token_precision_expired", symbol=symbol)
            self._token_precision.pop(symbol, None)
            self._save_file(TOKEN_PRECISION_FILE, self._token_precision)
            return None
        return item.data

    def set_token_precision(self, symbol_short: str, data: dict[str, Any]) -> None:
        symbol = symbol_short.upper()
        self._token_precision[symbol] = CachedItem(data=data, cached_at=datetime.now())
        self._save_file(TOKEN_PRECISION_FILE, self._token_precision)

    def set_all_token_precision(self, items: dict[str, dict[str, Any]]) -> None:
        now = datetime.now()
        for symbol, data in items.items():
            symbol_upper = symbol.upper()
            self._token_precision[symbol_upper] = CachedItem(data=data, cached_at=now)
        self._save_file(TOKEN_PRECISION_FILE, self._token_precision)
