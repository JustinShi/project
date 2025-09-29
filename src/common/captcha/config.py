"""验证码服务配置管理"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class CaptchaConfig:
    """验证码服务配置管理"""

    def __init__(
        self, service_name: str, config_file: Optional[str] = None, env: str = "default"
    ):
        """
        初始化配置

        Args:
            service_name: 服务名称 (chaojiying, ruokuai, 2captcha, local)
            config_file: 配置文件路径, 如果为 None 则自动查找
            env: 环境名称 (default, development, testing, production)
        """
        self.service_name = service_name
        self.env = env
        self.config_file = config_file or self._find_config_file()
        self._config = self._load_config()

    def _find_config_file(self) -> str:
        """查找配置文件"""
        # 可能的配置文件路径
        possible_paths = [
            # 项目根目录下的配置文件
            f"configs/captcha/{self.service_name}.yaml",
            # 环境特定的配置文件
            f"configs/environments/{self.env}/captcha/{self.service_name}.yaml",
            # 用户主目录下的配置文件
            f"~/.config/captcha/{self.service_name}.yaml",
            # 当前目录下的配置文件
            f"{self.service_name}.yaml",
        ]

        for path in possible_paths:
            expanded_path = Path(path).expanduser()
            if expanded_path.exists():
                return str(expanded_path)

        # 如果没有找到配置文件, 创建默认配置
        return self._create_default_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not self.config_file or not Path(self.config_file).exists():
            return self._get_default_config()

        try:
            with open(self.config_file, encoding="utf-8") as f:
                config = yaml.safe_load(f)
                return config or {}
        except Exception as e:
            print(f"警告: 无法加载配置文件 {self.config_file}: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "timeout": 30,
            "max_retries": 3,
            "upload_url": "",
            "report_url": "",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "default_codetype": "1902",
            "supported_codetypes": {
                "1902": "通用数字英文验证码",
                "1004": "4位纯数字验证码",
                "1005": "5位纯数字验证码",
                "1006": "6位纯数字验证码",
                "2004": "4位纯英文验证码",
                "3004": "4位英文数字验证码",
                "3005": "5位英文数字验证码",
                "3006": "6位英文数字验证码",
                "4004": "4位纯中文验证码",
                "5000": "无类型验证码",
            },
            "advanced": {
                "enable_retry": True,
                "retry_delay": 1.0,
                "max_retry_delay": 10.0,
                "retry_backoff_factor": 2.0,
            },
        }

    def _create_default_config(self) -> str:
        """创建默认配置文件"""
        config_dir = Path("configs/captcha")
        config_dir.mkdir(parents=True, exist_ok=True)

        config_file = config_dir / f"{self.service_name}.yaml"
        default_config = self._get_default_config()

        try:
            with open(config_file, "w", encoding="utf-8") as f:
                yaml.dump(
                    default_config, f, default_flow_style=False, allow_unicode=True
                )
            print(f"已创建默认配置文件: {config_file}")
            return str(config_file)
        except Exception as e:
            print(f"警告: 无法创建默认配置文件: {e}")
            return ""

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_credentials(self) -> Dict[str, str]:
        """获取认证凭据(从环境变量)"""
        env_prefix = self.service_name.upper()
        credentials = {}

        # 常见的凭据字段
        credential_fields = ["username", "password", "api_key", "secret", "soft_id"]

        for field in credential_fields:
            env_var = f"{env_prefix}_{field.upper()}"
            value = os.getenv(env_var)
            if value:
                credentials[field] = value

        return credentials

    def get_upload_url(self) -> str:
        """获取上传URL"""
        return self.get("upload_url", "")

    def get_report_url(self) -> str:
        """获取报告URL"""
        return self.get("report_url", "")

    def get_timeout(self) -> int:
        """获取超时时间"""
        return self.get("timeout", 30)

    def get_max_retries(self) -> int:
        """获取最大重试次数"""
        return self.get("max_retries", 3)

    def get_user_agent(self) -> str:
        """获取用户代理"""
        return self.get(
            "user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )

    def get_default_codetype(self) -> str:
        """获取默认验证码类型"""
        return self.get("default_codetype", "1902")

    def get_supported_codetypes(self) -> Dict[str, str]:
        """获取支持的验证码类型"""
        return self.get("supported_codetypes", {})

    def get_advanced_config(self) -> Dict[str, Any]:
        """获取高级配置"""
        return self.get("advanced", {})

    def is_retry_enabled(self) -> bool:
        """是否启用重试"""
        return self.get("advanced.enable_retry", True)

    def get_retry_delay(self) -> float:
        """获取重试延迟"""
        return self.get("advanced.retry_delay", 1.0)

    def get_max_retry_delay(self) -> float:
        """获取最大重试延迟"""
        return self.get("advanced.max_retry_delay", 10.0)

    def get_retry_backoff_factor(self) -> float:
        """获取重试退避因子"""
        return self.get("advanced.retry_backoff_factor", 2.0)

    def validate_config(self) -> bool:
        """验证配置是否有效"""
        required_fields = ["upload_url", "report_url"]

        for field in required_fields:
            if not self.get(field):
                print(f"警告: 缺少必需的配置字段: {field}")
                return False

        return True

    def __str__(self) -> str:
        """字符串表示"""
        return f"CaptchaConfig(service={self.service_name}, env={self.env}, file={self.config_file})"

    def __repr__(self) -> str:
        """详细字符串表示"""
        return self.__str__()
