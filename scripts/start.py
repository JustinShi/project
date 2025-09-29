#!/usr/bin/env python3
"""
My Platform 启动脚本
用于快速启动各个子项目
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent


def run_command(cmd, description):
    """运行命令并显示描述"""
    print(f"\n🚀 {description}")
    print(f"执行命令: {cmd}")
    print("-" * 50)

    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令执行失败: {e}")
        if e.stderr:
            print(f"错误输出: {e.stderr}")
        return False


def check_dependencies():
    """检查依赖是否安装"""
    print("🔍 检查依赖...")

    # 检查uv是否安装
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
        print("✅ uv 已安装")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ uv 未安装, 请先安装 uv")
        print("安装命令: pip install uv")
        return False

    return True


def install_dependencies():
    """安装项目依赖"""
    print("\n📦 安装项目依赖...")

    if not check_dependencies():
        return False

    # 安装根项目依赖
    if not run_command("uv sync", "安装根项目依赖"):
        return False

    # 安装交易项目依赖
    trading_path = PROJECT_ROOT / "projects" / "trading"
    if trading_path.exists():
        os.chdir(trading_path)
        if not run_command("uv sync", "安装交易项目依赖"):
            return False
        os.chdir(PROJECT_ROOT)

    print("✅ 依赖安装完成")
    return True


def start_services():
    """启动基础服务"""
    print("\n🐳 启动基础服务...")

    # 检查Docker是否运行
    try:
        subprocess.run(["docker", "version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker 未运行或未安装")
        print("请确保 Docker Desktop 正在运行")
        return False

    # 启动Redis
    if not run_command("docker-compose up -d redis", "启动Redis服务"):
        return False

    print("✅ 基础服务启动完成")
    return True


def start_project(project_name):
    """启动指定项目"""
    print(f"\n🚀 启动 {project_name} 项目...")

    project_path = PROJECT_ROOT / "projects" / project_name

    if not project_path.exists():
        print(f"❌ 项目 {project_name} 不存在")
        return False

    # 切换到项目目录
    os.chdir(project_path)

    # 启动项目
    if project_name == "trading":
        cmd = "uv run python main.py"
    else:
        cmd = "uv run python main.py"

    try:
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        print(f"\n⏹️  {project_name} 项目已停止")

    # 返回根目录
    os.chdir(PROJECT_ROOT)
    return True


def run_tests():
    """运行测试"""
    print("\n🧪 运行测试...")

    # 运行所有测试
    if not run_command("uv run pytest tests/ -v", "运行所有测试"):
        return False

    print("✅ 测试完成")
    return True


def show_status():
    """显示项目状态"""
    print("\n📊 项目状态...")

    # 检查依赖状态
    print("\n📦 依赖状态:")
    if check_dependencies():
        print("✅ 依赖已安装")
    else:
        print("❌ 依赖未安装")

    # 检查服务状态
    print("\n🐳 服务状态:")
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=redis"], capture_output=True, text=True
        )
        if "redis" in result.stdout:
            print("✅ Redis 正在运行")
        else:
            print("❌ Redis 未运行")
    except Exception as e:
        print(f"❌ 无法检查服务状态: {e}")

    # 检查项目状态
    print("\n📁 项目状态:")
    projects = ["trading", "crawler", "analyzer"]
    for project in projects:
        project_path = PROJECT_ROOT / "projects" / project
        if project_path.exists():
            print(f"✅ {project} 项目存在")
        else:
            print(f"❌ {project} 项目不存在")


def run_http_example():
    """运行 HTTP 客户端示例"""
    print("\n🌐 运行 HTTP 客户端示例...")

    example_path = PROJECT_ROOT / "examples" / "http_client_usage.py"

    if not example_path.exists():
        print("❌ HTTP 客户端示例文件不存在")
        return False

    if not run_command(f"python {example_path}", "运行 HTTP 客户端示例"):
        return False

    print("✅ HTTP 客户端示例运行完成")
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="My Platform 启动脚本")
    parser.add_argument(
        "action",
        choices=[
            "install",
            "start",
            "trading",
            "crawler",
            "analyzer",
            "test",
            "status",
            "http-example",
            "format",
            "check",
        ],
        help="要执行的操作",
    )

    args = parser.parse_args()

    if args.action == "install":
        if not install_dependencies():
            sys.exit(1)
        print("\n✅ 依赖安装完成")

    elif args.action == "start":
        if not start_services():
            sys.exit(1)
        print("\n✅ 基础服务启动完成")

    elif args.action in ["trading", "crawler", "analyzer"]:
        if not start_project(args.action):
            sys.exit(1)

    elif args.action == "test":
        if not run_tests():
            sys.exit(1)

    elif args.action == "status":
        show_status()

    elif args.action == "http-example":
        if not run_http_example():
            sys.exit(1)

    elif args.action == "format":
        handle_format()

    elif args.action == "check":
        handle_check()


def handle_format():
    """处理代码格式化操作"""
    print("🎨 格式化代码...")
    if not run_command("make format", "代码格式化"):
        sys.exit(1)


def handle_check():
    """处理代码质量检查"""
    print("🔍 代码质量检查...")
    if not run_command("make quality", "代码质量检查"):
        sys.exit(1)


def show_usage():
    """显示使用说明"""
    print("\n🎯 使用说明:")
    print("1. 首次使用: python start.py install")
    print("2. 启动服务: python start.py start")
    print("3. 运行项目: python start.py trading")
    print("4. 运行测试: python start.py test")
    print("5. 代码质量检查: python start.py check")
    print("6. 格式化代码: python start.py format")
    print("7. 查看状态: python start.py status")
    print("8. 运行 HTTP 示例: python start.py http-example")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        show_usage()
    else:
        main()
