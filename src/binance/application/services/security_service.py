"""安全服务"""

import re
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from binance.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SecurityConfig:
    """安全配置"""
    # API访问控制
    max_requests_per_minute: int = 60
    max_requests_per_hour: int = 1000
    max_requests_per_day: int = 10000
    
    # 敏感数据脱敏
    mask_headers: bool = True
    mask_cookies: bool = True
    mask_credit_cards: bool = True
    mask_emails: bool = False
    
    # 加密密钥轮换
    key_rotation_days: int = 30
    key_transition_days: int = 7
    
    # 审计日志
    audit_all_operations: bool = True
    audit_sensitive_data: bool = True
    audit_retention_days: int = 90


class SecurityService:
    """安全服务"""
    
    def __init__(self, config: Optional[SecurityConfig] = None):
        self.config = config or SecurityConfig()
        self._rate_limits: Dict[str, List[datetime]] = {}
        self._audit_logs: List[Dict[str, Any]] = []
    
    def check_rate_limit(self, user_id: int, endpoint: str) -> tuple[bool, str]:
        """检查API访问频率限制"""
        key = f"{user_id}:{endpoint}"
        now = datetime.now()
        
        # 清理过期记录
        if key in self._rate_limits:
            self._rate_limits[key] = [
                timestamp for timestamp in self._rate_limits[key]
                if now - timestamp < timedelta(days=1)
            ]
        else:
            self._rate_limits[key] = []
        
        # 检查限制
        recent_requests = self._rate_limits[key]
        
        # 每分钟限制
        minute_ago = now - timedelta(minutes=1)
        minute_requests = [r for r in recent_requests if r > minute_ago]
        if len(minute_requests) >= self.config.max_requests_per_minute:
            return False, f"每分钟请求次数超过限制 {self.config.max_requests_per_minute}"
        
        # 每小时限制
        hour_ago = now - timedelta(hours=1)
        hour_requests = [r for r in recent_requests if r > hour_ago]
        if len(hour_requests) >= self.config.max_requests_per_hour:
            return False, f"每小时请求次数超过限制 {self.config.max_requests_per_hour}"
        
        # 每天限制
        day_ago = now - timedelta(days=1)
        day_requests = [r for r in recent_requests if r > day_ago]
        if len(day_requests) >= self.config.max_requests_per_day:
            return False, f"每天请求次数超过限制 {self.config.max_requests_per_day}"
        
        # 记录请求
        recent_requests.append(now)
        self._rate_limits[key] = recent_requests
        
        return True, "访问频率检查通过"
    
    def mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """脱敏敏感数据"""
        masked_data = data.copy()
        
        # 脱敏headers
        if self.config.mask_headers and "headers" in masked_data:
            headers = masked_data["headers"]
            if isinstance(headers, str):
                # 简单脱敏：保留前几位和后几位
                if len(headers) > 10:
                    masked_data["headers"] = f"{headers[:3]}***{headers[-3:]}"
                else:
                    masked_data["headers"] = "***"
            elif isinstance(headers, dict):
                masked_data["headers"] = {k: "***" for k in headers.keys()}
        
        # 脱敏cookies
        if self.config.mask_cookies and "cookies" in masked_data:
            cookies = masked_data["cookies"]
            if isinstance(cookies, str):
                if len(cookies) > 10:
                    masked_data["cookies"] = f"{cookies[:3]}***{cookies[-3:]}"
                else:
                    masked_data["cookies"] = "***"
        
        # 脱敏信用卡号
        if self.config.mask_credit_cards:
            for key, value in masked_data.items():
                if isinstance(value, str) and self._is_credit_card(value):
                    masked_data[key] = self._mask_credit_card(value)
        
        # 脱敏邮箱
        if self.config.mask_emails:
            for key, value in masked_data.items():
                if isinstance(value, str) and self._is_email(value):
                    masked_data[key] = self._mask_email(value)
        
        return masked_data
    
    def _is_credit_card(self, text: str) -> bool:
        """检查是否为信用卡号"""
        # 简单的信用卡号检测（13-19位数字）
        cleaned = re.sub(r'\D', '', text)
        return len(cleaned) >= 13 and len(cleaned) <= 19
    
    def _mask_credit_card(self, card_number: str) -> str:
        """脱敏信用卡号"""
        cleaned = re.sub(r'\D', '', card_number)
        if len(cleaned) >= 8:
            return f"{cleaned[:4]}****{cleaned[-4:]}"
        return "****"
    
    def _is_email(self, text: str) -> bool:
        """检查是否为邮箱"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, text))
    
    def _mask_email(self, email: str) -> str:
        """脱敏邮箱"""
        if '@' in email:
            local, domain = email.split('@', 1)
            if len(local) > 2:
                masked_local = f"{local[0]}***{local[-1]}"
            else:
                masked_local = "***"
            return f"{masked_local}@{domain}"
        return "***"
    
    def generate_secure_token(self, length: int = 32) -> str:
        """生成安全令牌"""
        return secrets.token_urlsafe(length)
    
    def hash_password(self, password: str) -> str:
        """哈希密码"""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{hash_obj.hex()}"
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """验证密码"""
        try:
            salt, hash_hex = hashed.split(':', 1)
            hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return hash_obj.hex() == hash_hex
        except ValueError:
            return False
    
    def log_audit_event(
        self, 
        user_id: int, 
        action: str, 
        resource: str, 
        details: Optional[Dict[str, Any]] = None,
        sensitive_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """记录审计日志"""
        if not self.config.audit_all_operations:
            return
        
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "details": details or {},
            "ip_address": "127.0.0.1",  # 实际应用中从请求中获取
            "user_agent": "system",  # 实际应用中从请求中获取
        }
        
        # 处理敏感数据
        if sensitive_data and self.config.audit_sensitive_data:
            audit_entry["sensitive_data"] = self.mask_sensitive_data(sensitive_data)
        
        self._audit_logs.append(audit_entry)
        
        # 限制审计日志数量
        if len(self._audit_logs) > 10000:
            self._audit_logs = self._audit_logs[-5000:]
        
        logger.info(f"审计日志: 用户 {user_id} 执行 {action} 操作", extra=audit_entry)
    
    def get_audit_logs(
        self, 
        user_id: Optional[int] = None, 
        action: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取审计日志"""
        logs = self._audit_logs.copy()
        
        # 过滤条件
        if user_id is not None:
            logs = [log for log in logs if log.get("user_id") == user_id]
        
        if action is not None:
            logs = [log for log in logs if log.get("action") == action]
        
        if start_time is not None:
            logs = [log for log in logs if datetime.fromisoformat(log["timestamp"]) >= start_time]
        
        if end_time is not None:
            logs = [log for log in logs if datetime.fromisoformat(log["timestamp"]) <= end_time]
        
        # 按时间倒序排列
        logs.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return logs[:limit]
    
    def validate_input(self, data: Dict[str, Any], rules: Dict[str, Any]) -> tuple[bool, List[str]]:
        """验证输入数据"""
        errors = []
        
        for field, rule in rules.items():
            if field not in data:
                if rule.get("required", False):
                    errors.append(f"字段 {field} 是必需的")
                continue
            
            value = data[field]
            field_type = rule.get("type")
            
            # 类型检查
            if field_type == "string" and not isinstance(value, str):
                errors.append(f"字段 {field} 必须是字符串")
            elif field_type == "integer" and not isinstance(value, int):
                errors.append(f"字段 {field} 必须是整数")
            elif field_type == "decimal" and not isinstance(value, (int, float)):
                errors.append(f"字段 {field} 必须是数字")
            elif field_type == "boolean" and not isinstance(value, bool):
                errors.append(f"字段 {field} 必须是布尔值")
            
            # 长度检查
            if isinstance(value, str):
                min_length = rule.get("min_length", 0)
                max_length = rule.get("max_length")
                if len(value) < min_length:
                    errors.append(f"字段 {field} 长度不能少于 {min_length}")
                if max_length and len(value) > max_length:
                    errors.append(f"字段 {field} 长度不能超过 {max_length}")
            
            # 数值范围检查
            if isinstance(value, (int, float)):
                min_value = rule.get("min_value")
                max_value = rule.get("max_value")
                if min_value is not None and value < min_value:
                    errors.append(f"字段 {field} 值不能小于 {min_value}")
                if max_value is not None and value > max_value:
                    errors.append(f"字段 {field} 值不能超过 {max_value}")
            
            # 正则表达式检查
            pattern = rule.get("pattern")
            if pattern and isinstance(value, str):
                if not re.match(pattern, value):
                    errors.append(f"字段 {field} 格式不正确")
        
        return len(errors) == 0, errors
    
    def sanitize_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """清理输入数据"""
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                # 移除潜在的恶意字符
                sanitized_value = re.sub(r'[<>"\']', '', value)
                sanitized_value = sanitized_value.strip()
                sanitized[key] = sanitized_value
            else:
                sanitized[key] = value
        
        return sanitized
    
    def check_permissions(self, user_id: int, resource: str, action: str) -> bool:
        """检查用户权限"""
        # 简单的权限检查逻辑
        # 实际应用中应该从数据库或缓存中获取用户权限
        
        # 管理员权限
        if user_id == 1:  # 假设用户1是管理员
            return True
        
        # 普通用户权限
        allowed_actions = {
            "users": ["read", "update"],
            "configs": ["read", "create", "update"],
            "orders": ["read", "create", "update"],
            "notifications": ["read", "update"],
            "risk": ["read"],
            "monitoring": ["read"]
        }
        
        if resource in allowed_actions:
            return action in allowed_actions[resource]
        
        return False
    
    def get_security_summary(self) -> Dict[str, Any]:
        """获取安全摘要"""
        return {
            "rate_limits": {
                "active_limits": len(self._rate_limits),
                "max_requests_per_minute": self.config.max_requests_per_minute,
                "max_requests_per_hour": self.config.max_requests_per_hour,
                "max_requests_per_day": self.config.max_requests_per_day
            },
            "audit_logs": {
                "total_logs": len(self._audit_logs),
                "audit_enabled": self.config.audit_all_operations,
                "retention_days": self.config.audit_retention_days
            },
            "data_masking": {
                "mask_headers": self.config.mask_headers,
                "mask_cookies": self.config.mask_cookies,
                "mask_credit_cards": self.config.mask_credit_cards,
                "mask_emails": self.config.mask_emails
            },
            "key_rotation": {
                "rotation_days": self.config.key_rotation_days,
                "transition_days": self.config.key_transition_days
            }
        }
