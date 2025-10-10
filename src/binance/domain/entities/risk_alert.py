"""风险警报实体"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from enum import Enum

from binance.domain.entities.risk_profile import RiskLevel, RiskFactor


class AlertSeverity(str, Enum):
    """警报严重程度"""
    INFO = "INFO"         # 信息
    WARNING = "WARNING"   # 警告
    ERROR = "ERROR"       # 错误
    CRITICAL = "CRITICAL" # 严重


class AlertStatus(str, Enum):
    """警报状态"""
    ACTIVE = "ACTIVE"     # 活跃
    ACKNOWLEDGED = "ACKNOWLEDGED"  # 已确认
    RESOLVED = "RESOLVED" # 已解决
    DISMISSED = "DISMISSED"  # 已忽略


@dataclass
class RiskAlert:
    """风险警报"""
    
    id: int
    user_id: int
    
    # 警报基本信息
    title: str
    message: str
    severity: AlertSeverity
    risk_factor: RiskFactor
    risk_level: RiskLevel
    triggered_at: datetime
    
    # 可选字段
    status: AlertStatus = AlertStatus.ACTIVE
    current_value: Optional[Decimal] = None
    threshold_value: Optional[Decimal] = None
    data: Optional[Dict[str, Any]] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def acknowledge(self) -> None:
        """确认警报"""
        self.status = AlertStatus.ACKNOWLEDGED
        self.acknowledged_at = datetime.now()
        self.updated_at = datetime.now()
    
    def resolve(self) -> None:
        """解决警报"""
        self.status = AlertStatus.RESOLVED
        self.resolved_at = datetime.now()
        self.updated_at = datetime.now()
    
    def dismiss(self) -> None:
        """忽略警报"""
        self.status = AlertStatus.DISMISSED
        self.updated_at = datetime.now()
    
    def is_active(self) -> bool:
        """检查警报是否活跃"""
        return self.status == AlertStatus.ACTIVE
    
    def is_critical(self) -> bool:
        """检查是否为严重警报"""
        return self.severity == AlertSeverity.CRITICAL
    
    def get_duration(self) -> Optional[int]:
        """获取警报持续时间（秒）"""
        if self.status == AlertStatus.RESOLVED and self.resolved_at:
            return int((self.resolved_at - self.triggered_at).total_seconds())
        elif self.status in [AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED]:
            return int((datetime.now() - self.triggered_at).total_seconds())
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "message": self.message,
            "severity": self.severity.value,
            "status": self.status.value,
            "risk_factor": self.risk_factor.value,
            "risk_level": self.risk_level.value,
            "current_value": float(self.current_value) if self.current_value else None,
            "threshold_value": float(self.threshold_value) if self.threshold_value else None,
            "data": self.data,
            "triggered_at": self.triggered_at.isoformat(),
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "duration_seconds": self.get_duration()
        }
