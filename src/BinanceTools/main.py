"""
币安Alpha代币自动交易工具主程序

基于DDD架构的币安Alpha代币自动交易工具。
"""

import asyncio
import click
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from BinanceTools.interfaces.cli.cli_app import CliApp
from BinanceTools.interfaces.api.api_app import ApiApp
from BinanceTools.interfaces.sdk.sdk_client import SdkClient
from BinanceTools.interfaces.sdk.sdk_config import SdkConfig


@click.group()
def main():
    """币安Alpha代币自动交易工具"""
    pass


@main.command()
def cli():
    """启动CLI模式"""
    async def _run_cli():
        app = CliApp()
        try:
            await app.run()
        finally:
            await app.cleanup()
    
    asyncio.run(_run_cli())


@main.command()
@click.option('--host', default='0.0.0.0', help='API服务器主机')
@click.option('--port', default=8000, help='API服务器端口')
def api(host: str, port: int):
    """启动API模式"""
    async def _run_api():
        app = ApiApp()
        try:
            await app.run(host, port)
        finally:
            await app.cleanup()
    
    asyncio.run(_run_api())


@main.command()
def sdk():
    """启动SDK模式"""
    async def _run_sdk():
        config = SdkConfig()
        
        # 检查配置
        if not config.validate_config():
            print("配置验证失败，请检查配置文件")
            return
        
        # 创建SDK客户端
        async with SdkClient(config) as client:
            print("SDK客户端已初始化")
            
            # 示例：获取用户列表
            user_config = config.get_user_config()
            users = user_config.get_active_users()
            
            if users:
                print(f"找到 {len(users)} 个活跃用户:")
                for user in users:
                    print(f"  - {user['name']} (ID: {user['id']})")
            else:
                print("没有找到活跃用户")
    
    asyncio.run(_run_sdk())


@main.command()
def version():
    """显示版本信息"""
    print("币安Alpha代币自动交易工具 v1.0.0")
    print("基于DDD架构设计")
    print("作者: BinanceTools Team")


@main.command()
def info():
    """显示项目信息"""
    print("币安Alpha代币自动交易工具")
    print("=" * 50)
    print("项目结构:")
    print("  - 领域层 (Domain): 核心业务逻辑")
    print("  - 应用层 (Application): 用例和应用服务")
    print("  - 基础设施层 (Infrastructure): 外部依赖")
    print("  - 接口层 (Interfaces): 用户接口")
    print("  - 共享层 (Shared): 共享组件")
    print()
    print("支持的功能:")
    print("  - 钱包余额查询")
    print("  - 订单管理 (下单、取消、查询)")
    print("  - 交易历史查询")
    print("  - 投资组合分析")
    print("  - 风险控制")
    print("  - 多种接口 (CLI、API、SDK)")
    print()
    print("使用方法:")
    print("  python -m BinanceTools.main cli     # 启动CLI模式")
    print("  python -m BinanceTools.main api     # 启动API模式")
    print("  python -m BinanceTools.main sdk     # 启动SDK模式")


if __name__ == "__main__":
    main()
