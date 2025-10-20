#!/usr/bin/env python3
"""日志清理脚本

定期清理超过保留期限的日志文件，避免磁盘空间占用过多。
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path


# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.binance.infrastructure.logging.logger import get_logger


logger = get_logger(__name__)


def cleanup_old_logs(logs_dir: str = "logs", retention_days: int = 7) -> None:
    """清理超过保留期限的日志文件

    Args:
        logs_dir: 日志目录路径
        retention_days: 保留天数，默认7天
    """
    logs_path = Path(logs_dir)
    if not logs_path.exists():
        logger.warning("日志目录不存在", logs_dir=logs_dir)
        return

    # 计算截止日期
    cutoff_date = datetime.now() - timedelta(days=retention_days)

    # 查找所有日志文件
    log_files = []
    for pattern in ["*.log", "*.log.*"]:
        log_files.extend(logs_path.glob(pattern))

    deleted_count = 0
    total_size_freed = 0

    for log_file in log_files:
        try:
            # 获取文件修改时间
            file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)

            # 如果文件超过保留期限，删除它
            if file_mtime < cutoff_date:
                file_size = log_file.stat().st_size
                log_file.unlink()

                deleted_count += 1
                total_size_freed += file_size

                logger.info(
                    "删除过期日志文件",
                    file_path=str(log_file),
                    file_size=f"{file_size / 1024 / 1024:.2f}MB",
                    file_age_days=(datetime.now() - file_mtime).days,
                )

        except Exception as e:
            logger.error("删除日志文件失败", file_path=str(log_file), error=str(e))

    if deleted_count > 0:
        logger.info(
            "日志清理完成",
            deleted_files=deleted_count,
            total_size_freed=f"{total_size_freed / 1024 / 1024:.2f}MB",
        )
    else:
        logger.info("没有需要清理的日志文件")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="清理过期日志文件")
    parser.add_argument("--logs-dir", default="logs", help="日志目录路径 (默认: logs)")
    parser.add_argument(
        "--retention-days", type=int, default=7, help="保留天数 (默认: 7天)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="只显示将要删除的文件，不实际删除"
    )

    args = parser.parse_args()

    if args.dry_run:
        logger.info("干运行模式：只显示将要删除的文件")
        # TODO: 实现干运行模式
        return

    logger.info(
        "开始清理日志文件", logs_dir=args.logs_dir, retention_days=args.retention_days
    )

    cleanup_old_logs(args.logs_dir, args.retention_days)


if __name__ == "__main__":
    main()
