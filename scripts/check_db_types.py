"""检查数据库中的数据类型"""

import sqlite3
from pathlib import Path


def main():
    db_path = Path(__file__).parent.parent / "data" / "binance.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("Users 表结构:")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]}: {col[2]}")
    print()

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("Headers 数据类型:")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    cursor.execute("SELECT id, typeof(headers), length(headers) FROM users")
    results = cursor.fetchall()
    for user_id, type_name, length in results:
        print(f"  user_id={user_id}: {type_name}, length={length}")
    print()

    conn.close()


if __name__ == "__main__":
    main()
