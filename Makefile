.PHONY: help install format check lint test clean clean-all pre-commit-install pre-commit-run run-strategy

help:  ## 显示帮助信息
	@echo "可用的命令:"
	@echo ""
	@echo "Ruff 命令 (推荐):"
	@echo "ruff             - 运行 Ruff 检查"
	@echo "ruff-fix         - 运行 Ruff 检查并自动修复"
	@echo "ruff-format      - 运行 Ruff 格式化"
	@echo "ruff-all         - 运行 Ruff 完整检查（格式化 + 检查 + 修复）"
	@echo ""
	@echo "通用命令:"
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
	@echo "交易脚本:"
	@echo "run-strategy           - 运行指定策略 (默认模式)"
	@echo "run-strategy-quiet     - 运行指定策略 (安静模式，只显示结果)"
	@echo "run-strategy-debug     - 运行指定策略 (调试模式，显示详细日志)"
	@echo "run-all-strategies     - 运行所有启用的策略 (推荐)"
	@echo "run-all-strategies-quiet - 运行所有启用的策略 (安静模式)"
	@echo "run-all-strategies-debug - 运行所有启用的策略 (调试模式)"
	@echo "check-volumes          - 查询所有用户的实际交易量 (并行查询)"
	@echo ""
	@echo "清理命令:"
	@echo "clean            - 清理临时文件"
	@echo "clean-all        - 深度清理所有冗余文件"
	@echo ""
	@echo "其他命令:"
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
	uv run bandit -r src/ scripts/ -f json -o bandit-report.json --skip B101,B104,B105,B110

check-types:  ## 检查类型注解
	uv run mypy src/ --ignore-missing-imports --no-strict-optional

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
	uv run bandit -r src/ scripts/ -f json -o bandit-report.json --skip B101,B104,B105,B110
	@echo "✓ 代码质量检查通过"

type-check:  ## 运行类型检查 (MyPy)
	uv run mypy src/ --ignore-missing-imports --no-strict-optional

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
	@echo "清理临时文件..."
	uv run python scripts/cleanup.py
	@if exist .coverage del .coverage 2>nul
	@if exist htmlcov rmdir /s /q htmlcov 2>nul
	@if exist .mypy_cache rmdir /s /q .mypy_cache 2>nul
	@if exist bandit-report.json del bandit-report.json 2>nul
	@echo "清理完成！"

clean-all:  ## 深度清理所有冗余文件
	@echo "深度清理所有冗余文件..."
	@make clean
	@if exist .venv rmdir /s /q .venv 2>nul
	@if exist uv.lock del uv.lock 2>nul
	@if exist dist rmdir /s /q dist 2>nul
	@if exist build rmdir /s /q build 2>nul
	@if exist *.egg-info rmdir /s /q *.egg-info 2>nul
	@echo "深度清理完成！"

pre-commit-install:  ## 安装 pre-commit hooks
	uv run pre-commit install

pre-commit-run:  ## 运行 pre-commit 检查
	uv run pre-commit run --all-files

# ==================== 交易脚本 ====================

run-strategy:  ## 运行交易策略 (使用: make run-strategy STRATEGY=策略名)
ifndef STRATEGY
	@echo "错误: 请指定策略名称"
	@echo "用法: make run-strategy STRATEGY=aop_test"
	@echo ""
	@echo "示例:"
	@echo "  make run-strategy STRATEGY=aop_test          # 默认模式"
	@echo "  make run-strategy-quiet STRATEGY=aop_test    # 安静模式"
	@echo "  make run-strategy-debug STRATEGY=aop_test    # 调试模式"
	@exit 1
endif
	@echo "启动交易策略: $(STRATEGY)"
	@echo ""
	@set LOG_FORMAT=console && uv run python scripts/run_trading_strategy.py --strategy $(STRATEGY)

run-strategy-quiet:  ## 安静模式运行策略（只显示最终结果）
ifndef STRATEGY
	@echo "错误: 请指定策略名称"
	@echo "用法: make run-strategy-quiet STRATEGY=aop_test"
	@exit 1
endif
	@echo "安静模式启动策略: $(STRATEGY)"
	@echo ""
	@set LOG_FORMAT=console && uv run python scripts/run_trading_strategy.py --strategy $(STRATEGY) --quiet

run-strategy-debug:  ## 调试模式运行策略（显示详细日志）
ifndef STRATEGY
	@echo "错误: 请指定策略名称"
	@echo "用法: make run-strategy-debug STRATEGY=aop_test"
	@exit 1
endif
	@echo "调试模式启动策略: $(STRATEGY)"
	@echo ""
	@set LOG_LEVEL=DEBUG && set LOG_FORMAT=console && uv run python scripts/run_trading_strategy.py --strategy $(STRATEGY)

run-all-strategies:  ## 运行所有启用的策略
	@echo "启动所有启用的策略"
	@echo ""
	@set LOG_FORMAT=console && uv run python scripts/run_trading_strategy.py

run-all-strategies-quiet:  ## 运行所有启用的策略（安静模式）
	@echo "安静模式启动所有策略"
	@echo ""
	@set LOG_FORMAT=console && uv run python scripts/run_trading_strategy.py --quiet

run-all-strategies-debug:  ## 运行所有启用的策略（调试模式）
	@echo "调试模式启动所有策略"
	@echo ""
	@set LOG_LEVEL=DEBUG && set LOG_FORMAT=console && uv run python scripts/run_trading_strategy.py


check-volumes:  ## 查询所有用户的实际交易量 (使用: make check-volumes TOKEN=代币符号)
	@echo "查询所有用户交易量"
	@echo "不指定TOKEN时显示所有代币，指定TOKEN时只显示该代币"
	@echo ""
ifdef TOKEN
	uv run python scripts/check_all_users_volume.py $(TOKEN)
else
	uv run python scripts/check_all_users_volume.py
endif

cleanup-logs:  ## 清理过期日志文件 (使用: make cleanup-logs DAYS=保留天数)
	@echo "清理过期日志文件"
	@echo ""
ifdef DAYS
	uv run python scripts/cleanup_logs.py --retention-days $(DAYS)
else
	uv run python scripts/cleanup_logs.py
endif

check-user-volume:  ## 检查指定用户的交易量 (使用: make check-user-volume USER_ID=用户ID TOKEN=代币符号)
	@echo "检查用户交易量"
	@echo ""
ifdef USER_ID
ifdef TOKEN
	uv run python scripts/check_all_users_volume.py $(TOKEN) | findstr "用户 $(USER_ID)"
else
	uv run python scripts/check_all_users_volume.py | findstr "用户 $(USER_ID)"
endif
else
	@echo "请指定用户ID: make check-user-volume USER_ID=2"
endif



check-airdrop-scores:  ## 查询所有用户的空投积分
	@echo "查询所有用户的空投积分"
	@echo "只显示用户ID、姓名、总积分和查询日期"
	@echo ""
	uv run python scripts/simple_airdrop_scores.py
