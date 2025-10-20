"""清理项目临时文件和缓存"""

import shutil
from pathlib import Path


def cleanup_project():
    """清理项目中的临时文件和缓存"""
    project_root = Path(__file__).parent.parent

    cleaned_items = []

    # 1. 清理 __pycache__ 目录
    pycache_dirs = list(project_root.rglob("__pycache__"))
    for cache_dir in pycache_dirs:
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
            cleaned_items.append(str(cache_dir))

    # 2. 清理 .pytest_cache
    pytest_cache = project_root / ".pytest_cache"
    if pytest_cache.exists():
        shutil.rmtree(pytest_cache)
        cleaned_items.append(str(pytest_cache))

    # 3. 清理 .mypy_cache
    mypy_cache = project_root / ".mypy_cache"
    if mypy_cache.exists():
        shutil.rmtree(mypy_cache)
        cleaned_items.append(str(mypy_cache))

    # 4. 清理 .ruff_cache
    ruff_cache = project_root / ".ruff_cache"
    if ruff_cache.exists():
        shutil.rmtree(ruff_cache)
        cleaned_items.append(str(ruff_cache))

    # 5. 清理 bandit-report.json
    bandit_report = project_root / "bandit-report.json"
    if bandit_report.exists():
        bandit_report.unlink()
        cleaned_items.append(str(bandit_report))

    # 6. 清理根目录的 database.db（冗余文件）
    root_db = project_root / "database.db"
    if root_db.exists():
        root_db.unlink()
        cleaned_items.append(str(root_db))

    # 7. 清理 .pyc 文件
    pyc_files = list(project_root.rglob("*.pyc"))
    for pyc_file in pyc_files:
        if pyc_file.exists():
            pyc_file.unlink()
            cleaned_items.append(str(pyc_file))

    # 输出清理结果
    print("🧹 清理完成！")
    print(f"共清理 {len(cleaned_items)} 个项目：")

    # 按类型分组显示
    pycache_count = sum(1 for item in cleaned_items if "__pycache__" in item)
    pyc_count = sum(1 for item in cleaned_items if item.endswith(".pyc"))
    cache_count = sum(
        1
        for item in cleaned_items
        if any(c in item for c in [".pytest_cache", ".mypy_cache", ".ruff_cache"])
    )
    other_count = len(cleaned_items) - pycache_count - pyc_count - cache_count

    if pycache_count > 0:
        print(f"  - __pycache__ 目录: {pycache_count} 个")
    if pyc_count > 0:
        print(f"  - .pyc 文件: {pyc_count} 个")
    if cache_count > 0:
        print(f"  - 缓存目录: {cache_count} 个")
    if other_count > 0:
        print(f"  - 其他临时文件: {other_count} 个")


if __name__ == "__main__":
    cleanup_project()
