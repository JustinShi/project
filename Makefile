.PHONY: help install format check lint test clean clean-all pre-commit-install pre-commit-run run-strategy update-credentials

help:  ## 显示帮助信息
	@echo "可用的命令:"
	@echo ""
	@echo "🚀 Ruff 命令 (推荐):"
	@echo "ruff             - 运行 Ruff 检查"
	@echo "ruff-fix         - 运行 Ruff 检查并自动修复"
	@echo "ruff-format      - 运行 Ruff 格式化"
	@echo "ruff-all         - 运行 Ruff 完整检查（格式化 + 检查 + 修复）"
	@echo ""
	@echo "📋 通用命令:"
	@echo "install          - 安装项目依赖"
	@echo "format           - 格式化代码 (使用 Ruff)"
	@echo "check            - 检查代码格式（不修改）"
	@echo "check-format     - 仅检查代码格式"
	@echo "check-syntax     - 检查语法错误"
	@echo "check-style      - 检查代码风格"
	@echo "check-security   - 检查安全漏洞"
	@echo "check-types      - 检查类型注解"
	@echo "check-all        - 运行所有检查"
	@echo "lint             - 运行代码质量检查 (使用 Ruff)"
	@echo "test             - 运行测试"
	@echo "quality          - 运行完整的代码质量检查流程"
	@echo ""
	@echo "📈 交易脚本:"
	@echo "run-strategy     - 运行交易策略 (需要指定 STRATEGY=策略名)"
	@echo "update-credentials - 更新用户凭证"
	@echo ""
	@echo "🧹 清理命令:"
	@echo "clean            - 清理临时文件"
	@echo "clean-all        - 深度清理所有冗余文件"
	@echo ""
	@echo "🔧 其他命令:"
	@echo "pre-commit-install - 安装 pre-commit hooks"
	@echo "pre-commit-run   - 运行 pre-commit 检查"

install:  ## 安装项目依赖
	uv sync

format:  ## 格式化代码 (使用 Ruff)
	uv run ruff format .
	uv run ruff check --fix .

check:  ## 检查代码格式（不修改）
	uv run ruff format --check .
	uv run ruff check .

check-format:  ## 仅检查代码格式
	uv run ruff format --check .
	uv run ruff check .

check-syntax:  ## 检查语法错误
	uv run ruff check --select=E9,F63,F7,F82

check-style:  ## 检查代码风格
	uv run ruff check

check-security:  ## 检查安全漏洞
	uv run bandit -r . -f json -o bandit-report.json

check-types:  ## 检查类型注解
	uv run mypy . --ignore-missing-imports --no-strict-optional

check-all: check-format check-syntax check-style check-security check-types  ## 运行所有检查

ruff:  ## 运行 Ruff 检查
	uv run ruff check .

ruff-fix:  ## 运行 Ruff 检查并自动修复
	uv run ruff check --fix .

ruff-format:  ## 运行 Ruff 格式化
	uv run ruff format .

ruff-all:  ## 运行 Ruff 完整检查（格式化 + 检查 + 修复）
	uv run ruff format .
	uv run ruff check --fix .

lint:  ## 运行代码质量检查 (使用 Ruff)
	uv run ruff check .
	uv run bandit -r . -f json -o bandit-report.json
	uv run mypy . --ignore-missing-imports --no-strict-optional

test:  ## 运行测试
	uv run pytest tests/ -v

test-unit:  ## 运行单元测试
	uv run pytest tests/ -m "unit" -v

test-integration:  ## 运行集成测试
	uv run pytest tests/ -m "integration" -v

test-coverage:  ## 运行测试并生成覆盖率报告
	uv run pytest tests/ --cov=src --cov-report=html --cov-report=term

test-fast:  ## 运行快速测试（跳过慢速测试）
	uv run pytest tests/ -m "not slow" -v

test-all: test test-coverage  ## 运行所有测试和覆盖率检查

quality: format lint test  ## 运行完整的代码质量检查流程

clean:  ## 清理临时文件
	@echo "🧹 清理临时文件..."
	@if exist __pycache__ rmdir /s /q __pycache__ 2>nul
	@if exist .pytest_cache rmdir /s /q .pytest_cache 2>nul
	@if exist logs rmdir /s /q logs 2>nul
	@if exist *.log del *.log 2>nul
	@if exist .coverage del .coverage 2>nul
	@if exist htmlcov rmdir /s /q htmlcov 2>nul
	@if exist .mypy_cache rmdir /s /q .mypy_cache 2>nul
	@if exist bandit-report.json del bandit-report.json 2>nul
	@echo "✅ 清理完成！"

clean-all:  ## 深度清理所有冗余文件
	@echo "🧹 深度清理所有冗余文件..."
	@make clean
	@if exist .venv rmdir /s /q .venv 2>nul
	@if exist uv.lock del uv.lock 2>nul
	@if exist dist rmdir /s /q dist 2>nul
	@if exist build rmdir /s /q build 2>nul
	@if exist *.egg-info rmdir /s /q *.egg-info 2>nul
	@echo "✅ 深度清理完成！"

pre-commit-install:  ## 安装 pre-commit hooks
	uv run pre-commit install

pre-commit-run:  ## 运行 pre-commit 检查
	uv run pre-commit run --all-files

# ==================== 交易脚本 ====================

run-strategy:  ## 运行交易策略 (使用: make run-strategy STRATEGY=策略名)
ifndef STRATEGY
	@echo "❌ 错误: 请指定策略名称"
	@echo "用法: make run-strategy STRATEGY=aop_test"
	@echo ""
	@echo "示例:"
	@echo "  make run-strategy STRATEGY=aop_test"
	@exit 1
endif
	@echo "🚀 启动交易策略: $(STRATEGY)"
	@echo ""
	@set LOG_FORMAT=console && uv run python scripts/run_trading_strategy.py --strategy $(STRATEGY)

update-credentials:  ## 更新用户凭证
	@echo "🔐 启动用户凭证更新工具"
	@echo ""
	uv run python scripts/update_user_credentials_quick.py