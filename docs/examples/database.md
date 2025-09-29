# 🗄️ 数据库使用示例

本文档介绍 MySQL 和 PostgreSQL 在 Python 多项目平台中的使用方法和最佳实践。

## 📋 数据库概述

### 支持的数据库

- **MySQL**: 关系型数据库，适合 OLTP 场景
- **PostgreSQL**: 关系型数据库，功能强大，支持 JSON、数组等高级类型

### 数据库选择建议

- **MySQL**: 适合简单的业务逻辑，性能优秀，社区支持好
- **PostgreSQL**: 适合复杂查询，支持高级数据类型，扩展性强

## 🚀 快速开始

### 启动数据库服务

```bash
# 使用 Docker Compose 启动
docker-compose up -d mysql postgres

# 检查服务状态
docker-compose ps

# 查看日志
docker-compose logs mysql
docker-compose logs postgres
```

### 基本连接

```python
from common.storage.db_client import DatabaseManager

# 创建数据库管理器
db_manager = DatabaseManager()

# 测试连接
try:
    db_manager.ping()
    print("数据库连接成功")
except Exception as e:
    print(f"数据库连接失败: {e}")
```

## 🔧 基本操作

### 执行查询

```python
from common.storage.db_client import DatabaseManager

db_manager = DatabaseManager()

# 执行查询并返回所有结果
users = db_manager.query("SELECT * FROM users WHERE active = %s", (True,))
for user in users:
    print(f"用户: {user}")

# 执行查询并返回单条结果
user = db_manager.query_one("SELECT * FROM users WHERE id = %s", (1,))
if user:
    print(f"找到用户: {user}")
else:
    print("用户不存在")

# 执行更新操作
affected_rows = db_manager.execute(
    "UPDATE users SET last_login = %s WHERE id = %s",
    (datetime.now(), 1)
)
print(f"更新了 {affected_rows} 行")

# 批量插入
users_data = [
    ("张三", "zhangsan@example.com", "password123"),
    ("李四", "lisi@example.com", "password456"),
    ("王五", "wangwu@example.com", "password789")
]

affected_rows = db_manager.executemany(
    "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
    users_data
)
print(f"插入了 {affected_rows} 行")
```

### 使用连接上下文

```python
# 使用连接上下文管理器
with db_manager.get_connection() as conn:
    with conn.cursor() as cursor:
        # 执行查询
        cursor.execute("SELECT * FROM users LIMIT 10")
        users = cursor.fetchall()
        
        # 处理结果
        for user in users:
            print(f"用户: {user}")
        
        # 执行更新
        cursor.execute(
            "UPDATE users SET login_count = login_count + 1 WHERE id = %s",
            (1,)
        )
        
        # 提交事务
        conn.commit()
```

## 🏗️ 数据库设计

### 用户表设计

```sql
-- MySQL 用户表
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    login_count INT DEFAULT 0,
    
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_created_at (created_at),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- PostgreSQL 用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    login_count INTEGER DEFAULT 0,
    
    metadata JSONB DEFAULT '{}'::jsonb
);

-- 创建索引
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_active ON users(is_active);
CREATE INDEX idx_users_metadata ON users USING GIN(metadata);
```

### 订单表设计

```sql
-- MySQL 订单表
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    status ENUM('pending', 'paid', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
    total_amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'CNY',
    shipping_address TEXT,
    billing_address TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_order_number (order_number),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- PostgreSQL 订单表
CREATE TYPE order_status AS ENUM ('pending', 'paid', 'shipped', 'delivered', 'cancelled');

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    status order_status DEFAULT 'pending',
    total_amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'CNY',
    shipping_address TEXT,
    billing_address TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    metadata JSONB DEFAULT '{}'::jsonb,
    
    CONSTRAINT fk_orders_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_order_number ON orders(order_number);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_orders_metadata ON orders USING GIN(metadata);
```

## 🔧 数据操作

### 用户管理

```python
class UserManager:
    """用户管理器"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def create_user(self, username, email, password_hash, **kwargs):
        """创建用户"""
        sql = """
        INSERT INTO users (username, email, password_hash, first_name, last_name)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        first_name = kwargs.get('first_name', '')
        last_name = kwargs.get('last_name', '')
        
        try:
            user_id = self.db_manager.execute(
                sql, (username, email, password_hash, first_name, last_name)
            )
            return user_id
        except Exception as e:
            print(f"创建用户失败: {e}")
            return None
    
    def get_user_by_id(self, user_id):
        """根据ID获取用户"""
        sql = "SELECT * FROM users WHERE id = %s"
        return self.db_manager.query_one(sql, (user_id,))
    
    def get_user_by_username(self, username):
        """根据用户名获取用户"""
        sql = "SELECT * FROM users WHERE username = %s"
        return self.db_manager.query_one(sql, (username,))
    
    def get_user_by_email(self, email):
        """根据邮箱获取用户"""
        sql = "SELECT * FROM users WHERE email = %s"
        return self.db_manager.query_one(sql, (email,))
    
    def update_user(self, user_id, updates):
        """更新用户信息"""
        if not updates:
            return False
        
        # 构建动态更新SQL
        set_clauses = []
        values = []
        
        for field, value in updates.items():
            if field in ['username', 'email', 'first_name', 'last_name', 'is_active']:
                set_clauses.append(f"{field} = %s")
                values.append(value)
        
        if not set_clauses:
            return False
        
        sql = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = %s"
        values.append(user_id)
        
        try:
            affected_rows = self.db_manager.execute(sql, tuple(values))
            return affected_rows > 0
        except Exception as e:
            print(f"更新用户失败: {e}")
            return False
    
    def delete_user(self, user_id):
        """删除用户"""
        sql = "DELETE FROM users WHERE id = %s"
        try:
            affected_rows = self.db_manager.execute(sql, (user_id,))
            return affected_rows > 0
        except Exception as e:
            print(f"删除用户失败: {e}")
            return False
    
    def get_active_users(self, limit=100, offset=0):
        """获取活跃用户列表"""
        sql = """
        SELECT id, username, email, first_name, last_name, created_at, last_login
        FROM users 
        WHERE is_active = TRUE 
        ORDER BY created_at DESC 
        LIMIT %s OFFSET %s
        """
        return self.db_manager.query(sql, (limit, offset))
    
    def search_users(self, search_term, limit=100):
        """搜索用户"""
        sql = """
        SELECT id, username, email, first_name, last_name, created_at
        FROM users 
        WHERE username LIKE %s OR email LIKE %s OR first_name LIKE %s OR last_name LIKE %s
        ORDER BY created_at DESC 
        LIMIT %s
        """
        search_pattern = f"%{search_term}%"
        return self.db_manager.query(sql, (search_pattern, search_pattern, search_pattern, search_pattern, limit))
    
    def get_user_statistics(self):
        """获取用户统计信息"""
        sql = """
        SELECT 
            COUNT(*) as total_users,
            COUNT(CASE WHEN is_active = TRUE THEN 1 END) as active_users,
            COUNT(CASE WHEN created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY) THEN 1 END) as new_users_30d,
            COUNT(CASE WHEN last_login >= DATE_SUB(NOW(), INTERVAL 7 DAY) THEN 1 END) as active_users_7d
        FROM users
        """
        return self.db_manager.query_one(sql)

# 使用示例
user_manager = UserManager(db_manager)

# 创建用户
user_id = user_manager.create_user(
    username="zhangsan",
    email="zhangsan@example.com",
    password_hash="hashed_password_123",
    first_name="张三",
    last_name="张"
)

# 获取用户
user = user_manager.get_user_by_id(user_id)
print(f"创建的用户: {user}")

# 更新用户
updates = {"first_name": "张四", "last_name": "张"}
user_manager.update_user(user_id, updates)

# 搜索用户
users = user_manager.search_users("张")
print(f"搜索结果: {users}")

# 获取统计信息
stats = user_manager.get_user_statistics()
print(f"用户统计: {stats}")
```

### 订单管理

```python
class OrderManager:
    """订单管理器"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def create_order(self, user_id, order_number, total_amount, **kwargs):
        """创建订单"""
        sql = """
        INSERT INTO orders (user_id, order_number, total_amount, shipping_address, billing_address, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        shipping_address = kwargs.get('shipping_address', '')
        billing_address = kwargs.get('billing_address', '')
        notes = kwargs.get('notes', '')
        
        try:
            order_id = self.db_manager.execute(
                sql, (user_id, order_number, total_amount, shipping_address, billing_address, notes)
            )
            return order_id
        except Exception as e:
            print(f"创建订单失败: {e}")
            return None
    
    def get_order_by_id(self, order_id):
        """根据ID获取订单"""
        sql = """
        SELECT o.*, u.username, u.email
        FROM orders o
        JOIN users u ON o.user_id = u.id
        WHERE o.id = %s
        """
        return self.db_manager.query_one(sql, (order_id,))
    
    def get_user_orders(self, user_id, limit=100, offset=0):
        """获取用户订单列表"""
        sql = """
        SELECT * FROM orders 
        WHERE user_id = %s 
        ORDER BY created_at DESC 
        LIMIT %s OFFSET %s
        """
        return self.db_manager.query(sql, (user_id, limit, offset))
    
    def update_order_status(self, order_id, status):
        """更新订单状态"""
        sql = "UPDATE orders SET status = %s WHERE id = %s"
        try:
            affected_rows = self.db_manager.execute(sql, (status, order_id))
            return affected_rows > 0
        except Exception as e:
            print(f"更新订单状态失败: {e}")
            return False
    
    def get_orders_by_status(self, status, limit=100, offset=0):
        """根据状态获取订单"""
        sql = """
        SELECT o.*, u.username, u.email
        FROM orders o
        JOIN users u ON o.user_id = u.id
        WHERE o.status = %s
        ORDER BY o.created_at DESC
        LIMIT %s OFFSET %s
        """
        return self.db_manager.query(sql, (status, limit, offset))
    
    def get_order_statistics(self, days=30):
        """获取订单统计信息"""
        sql = """
        SELECT 
            COUNT(*) as total_orders,
            COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_orders,
            COUNT(CASE WHEN status = 'paid' THEN 1 END) as paid_orders,
            COUNT(CASE WHEN status = 'shipped' THEN 1 END) as shipped_orders,
            COUNT(CASE WHEN status = 'delivered' THEN 1 END) as delivered_orders,
            COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_orders,
            SUM(total_amount) as total_revenue,
            AVG(total_amount) as avg_order_value
        FROM orders 
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
        """
        return self.db_manager.query_one(sql, (days,))

# 使用示例
order_manager = OrderManager(db_manager)

# 创建订单
order_id = order_manager.create_order(
    user_id=1,
    order_number="ORD-2024-001",
    total_amount=299.99,
    shipping_address="北京市朝阳区xxx街道",
    billing_address="北京市朝阳区xxx街道"
)

# 获取订单
order = order_manager.get_order_by_id(order_id)
print(f"创建的订单: {order}")

# 更新订单状态
order_manager.update_order_status(order_id, "paid")

# 获取用户订单
user_orders = order_manager.get_user_orders(1)
print(f"用户订单: {user_orders}")

# 获取统计信息
order_stats = order_manager.get_order_statistics(30)
print(f"订单统计: {order_stats}")
```

## 🔄 事务管理

### 基本事务

```python
def transfer_money(from_account_id, to_account_id, amount):
    """转账操作"""
    try:
        # 开始事务
        db_manager.begin_transaction()
        
        # 检查源账户余额
        balance_sql = "SELECT balance FROM accounts WHERE id = %s FOR UPDATE"
        from_balance = db_manager.query_one(balance_sql, (from_account_id,))
        
        if not from_balance or from_balance['balance'] < amount:
            raise ValueError("余额不足")
        
        # 扣除源账户
        deduct_sql = "UPDATE accounts SET balance = balance - %s WHERE id = %s"
        db_manager.execute(deduct_sql, (amount, from_account_id))
        
        # 增加目标账户
        add_sql = "UPDATE accounts SET balance = balance + %s WHERE id = %s"
        db_manager.execute(add_sql, (amount, to_account_id))
        
        # 记录交易
        transaction_sql = """
        INSERT INTO transactions (from_account_id, to_account_id, amount, type, created_at)
        VALUES (%s, %s, %s, 'transfer', %s)
        """
        db_manager.execute(transaction_sql, (from_account_id, to_account_id, amount, datetime.now()))
        
        # 提交事务
        db_manager.commit_transaction()
        print(f"成功转账 {amount} 从账户 {from_account_id} 到账户 {to_account_id}")
        return True
        
    except Exception as e:
        # 回滚事务
        db_manager.rollback_transaction()
        print(f"转账失败: {e}")
        return False

# 使用示例
transfer_money(1, 2, 100.00)
```

### 嵌套事务

```python
def process_order_with_inventory(order_id):
    """处理订单和库存"""
    try:
        db_manager.begin_transaction()
        
        # 获取订单信息
        order_sql = "SELECT * FROM orders WHERE id = %s FOR UPDATE"
        order = db_manager.query_one(order_sql, (order_id,))
        
        if not order:
            raise ValueError("订单不存在")
        
        # 检查库存
        inventory_sql = "SELECT quantity FROM inventory WHERE product_id = %s FOR UPDATE"
        inventory = db_manager.query_one(inventory_sql, (order['product_id'],))
        
        if not inventory or inventory['quantity'] < order['quantity']:
            raise ValueError("库存不足")
        
        # 更新库存
        update_inventory_sql = "UPDATE inventory SET quantity = quantity - %s WHERE product_id = %s"
        db_manager.execute(update_inventory_sql, (order['quantity'], order['product_id']))
        
        # 更新订单状态
        update_order_sql = "UPDATE orders SET status = 'processing' WHERE id = %s"
        db_manager.execute(update_order_sql, (order_id,))
        
        # 记录库存变更
        inventory_log_sql = """
        INSERT INTO inventory_log (product_id, change_quantity, order_id, created_at)
        VALUES (%s, %s, %s, %s)
        """
        change_quantity = -order['quantity']  # 负数表示减少
        db_manager.execute(inventory_log_sql, (order['product_id'], change_quantity, order_id, datetime.now()))
        
        # 提交事务
        db_manager.commit_transaction()
        print(f"订单 {order_id} 处理成功")
        return True
        
    except Exception as e:
        # 回滚事务
        db_manager.rollback_transaction()
        print(f"订单处理失败: {e}")
        return False

# 使用示例
process_order_with_inventory(1)
```

## 📊 高级查询

### 复杂连接查询

```python
def get_user_order_summary(user_id):
    """获取用户订单摘要"""
    sql = """
    SELECT 
        u.id,
        u.username,
        u.email,
        COUNT(o.id) as total_orders,
        SUM(CASE WHEN o.status = 'delivered' THEN 1 ELSE 0 END) as completed_orders,
        SUM(CASE WHEN o.status = 'cancelled' THEN 1 ELSE 0 END) as cancelled_orders,
        SUM(o.total_amount) as total_spent,
        AVG(o.total_amount) as avg_order_value,
        MAX(o.created_at) as last_order_date,
        MIN(o.created_at) as first_order_date
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    WHERE u.id = %s
    GROUP BY u.id, u.username, u.email
    """
    
    return db_manager.query_one(sql, (user_id,))

def get_top_customers(limit=10):
    """获取顶级客户"""
    sql = """
    SELECT 
        u.id,
        u.username,
        u.email,
        COUNT(o.id) as order_count,
        SUM(o.total_amount) as total_spent,
        AVG(o.total_amount) as avg_order_value,
        MAX(o.created_at) as last_order_date
    FROM users u
    JOIN orders o ON u.id = o.user_id
    WHERE o.status != 'cancelled'
    GROUP BY u.id, u.username, u.email
    HAVING COUNT(o.id) >= 3
    ORDER BY total_spent DESC
    LIMIT %s
    """
    
    return db_manager.query(sql, (limit,))
```

### 子查询和窗口函数

```python
def get_user_rankings():
    """获取用户排名"""
    sql = """
    SELECT 
        user_id,
        username,
        total_spent,
        order_count,
        RANK() OVER (ORDER BY total_spent DESC) as spending_rank,
        RANK() OVER (ORDER BY order_count DESC) as order_rank,
        ROW_NUMBER() OVER (ORDER BY total_spent DESC) as row_num
    FROM (
        SELECT 
            u.id as user_id,
            u.username,
            SUM(o.total_amount) as total_spent,
            COUNT(o.id) as order_count
        FROM users u
        JOIN orders o ON u.id = o.user_id
        WHERE o.status != 'cancelled'
        GROUP BY u.id, u.username
    ) user_stats
    ORDER BY total_spent DESC
    """
    
    return db_manager.query(sql)

def get_monthly_revenue():
    """获取月度收入"""
    sql = """
    SELECT 
        DATE_FORMAT(created_at, '%Y-%m') as month,
        COUNT(*) as order_count,
        SUM(total_amount) as revenue,
        AVG(total_amount) as avg_order_value,
        LAG(SUM(total_amount)) OVER (ORDER BY DATE_FORMAT(created_at, '%Y-%m')) as prev_month_revenue,
        (SUM(total_amount) - LAG(SUM(total_amount)) OVER (ORDER BY DATE_FORMAT(created_at, '%Y-%m'))) / 
        LAG(SUM(total_amount)) OVER (ORDER BY DATE_FORMAT(created_at, '%Y-%m')) * 100 as growth_percentage
    FROM orders
    WHERE status = 'delivered'
    GROUP BY DATE_FORMAT(created_at, '%Y-%m')
    ORDER BY month
    """
    
    return db_manager.query(sql)
```

## 🔒 安全最佳实践

### 参数化查询

```python
# 正确的参数化查询
def get_user_by_credentials(username, password_hash):
    """根据凭据获取用户"""
    sql = "SELECT * FROM users WHERE username = %s AND password_hash = %s"
    return db_manager.query_one(sql, (username, password_hash))

# 错误的字符串拼接 (容易受到SQL注入攻击)
def get_user_by_credentials_unsafe(username, password_hash):
    """不安全的查询方式"""
    sql = f"SELECT * FROM users WHERE username = '{username}' AND password_hash = '{password_hash}'"
    return db_manager.query_one(sql)
```

### 权限控制

```python
class SecureUserManager:
    """安全的用户管理器"""
    
    def __init__(self, db_manager, current_user_id):
        self.db_manager = db_manager
        self.current_user_id = current_user_id
    
    def get_user_profile(self, user_id):
        """获取用户资料 (带权限检查)"""
        # 只能查看自己的资料或管理员可以查看所有
        if user_id != self.current_user_id and not self.is_admin():
            raise PermissionError("没有权限查看该用户资料")
        
        sql = "SELECT id, username, email, first_name, last_name, created_at FROM users WHERE id = %s"
        return self.db_manager.query_one(sql, (user_id,))
    
    def update_user_profile(self, user_id, updates):
        """更新用户资料 (带权限检查)"""
        # 只能更新自己的资料
        if user_id != self.current_user_id:
            raise PermissionError("没有权限更新该用户资料")
        
        # 限制可更新的字段
        allowed_fields = ['first_name', 'last_name', 'email']
        filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}
        
        if not filtered_updates:
            return False
        
        return self._update_user(user_id, filtered_updates)
    
    def is_admin(self):
        """检查当前用户是否为管理员"""
        sql = "SELECT is_admin FROM users WHERE id = %s"
        user = self.db_manager.query_one(sql, (self.current_user_id,))
        return user and user.get('is_admin', False)
    
    def _update_user(self, user_id, updates):
        """内部更新方法"""
        set_clauses = [f"{field} = %s" for field in updates.keys()]
        sql = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = %s"
        values = list(updates.values()) + [user_id]
        
        try:
            affected_rows = self.db_manager.execute(sql, tuple(values))
            return affected_rows > 0
        except Exception as e:
            print(f"更新用户失败: {e}")
            return False
```

## 📈 性能优化

### 索引优化

```sql
-- 创建复合索引
CREATE INDEX idx_orders_user_status_date ON orders(user_id, status, created_at);

-- 创建部分索引 (PostgreSQL)
CREATE INDEX idx_active_users ON users(username) WHERE is_active = TRUE;

-- 创建覆盖索引
CREATE INDEX idx_user_orders_covering ON orders(user_id, created_at, total_amount, status);

-- 创建函数索引 (PostgreSQL)
CREATE INDEX idx_users_email_lower ON users(LOWER(email));
```

### 查询优化

```python
def get_user_orders_optimized(user_id, limit=100, offset=0):
    """优化的用户订单查询"""
    # 使用 LIMIT 和 OFFSET 进行分页
    sql = """
    SELECT o.id, o.order_number, o.status, o.total_amount, o.created_at
    FROM orders o
    WHERE o.user_id = %s
    ORDER BY o.created_at DESC
    LIMIT %s OFFSET %s
    """
    
    return db_manager.query(sql, (user_id, limit, offset))

def get_user_orders_with_cursor(user_id, cursor=None, limit=100):
    """使用游标的分页查询"""
    if cursor:
        sql = """
        SELECT o.id, o.order_number, o.status, o.total_amount, o.created_at
        FROM orders o
        WHERE o.user_id = %s AND o.created_at < %s
        ORDER BY o.created_at DESC
        LIMIT %s
        """
        return db_manager.query(sql, (user_id, cursor, limit))
    else:
        sql = """
        SELECT o.id, o.order_number, o.status, o.total_amount, o.created_at
        FROM orders o
        WHERE o.user_id = %s
        ORDER BY o.created_at DESC
        LIMIT %s
        """
        return db_manager.query(sql, (user_id, limit))
```

### 连接池配置

```python
# 配置连接池
db_manager = DatabaseManager(
    host="localhost",
    port=3306,
    database="myplatform",
    username="myuser",
    password="mypassword",
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600
)
```

## 🚨 故障排除

### 常见问题

#### 1. 连接超时

```python
def check_database_connection():
    """检查数据库连接"""
    try:
        db_manager.ping()
        print("数据库连接正常")
        return True
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return False

# 定期检查连接
import time
while True:
    if not check_database_connection():
        print("尝试重新连接...")
        # 重新初始化连接
        db_manager = DatabaseManager()
    time.sleep(60)  # 每分钟检查一次
```

#### 2. 死锁处理

```python
def safe_transaction_operation(operation_func, max_retries=3):
    """安全的事务操作 (带重试)"""
    for attempt in range(max_retries):
        try:
            return operation_func()
        except Exception as e:
            if "Deadlock" in str(e) and attempt < max_retries - 1:
                print(f"检测到死锁，重试第 {attempt + 1} 次")
                time.sleep(0.1 * (2 ** attempt))  # 指数退避
                continue
            else:
                raise e

# 使用示例
def transfer_operation():
    return transfer_money(1, 2, 100.00)

result = safe_transaction_operation(transfer_operation)
```

#### 3. 性能监控

```python
import time
from functools import wraps

def measure_query_time(func):
    """测量查询时间的装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            if execution_time > 1.0:  # 超过1秒的查询
                print(f"慢查询警告: {func.__name__} 执行时间: {execution_time:.2f}秒")
            
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"查询失败: {func.__name__} 执行时间: {execution_time:.2f}秒, 错误: {e}")
            raise e
    
    return wrapper

# 使用装饰器
@measure_query_time
def get_user_orders_monitored(user_id):
    """带监控的用户订单查询"""
    return get_user_orders(user_id, 100, 0)
```

## 📚 下一步

- 查看 [存储模块 API](../api/storage.md)
- 了解 [Redis 使用示例](redis-usage.md)
- 阅读 [快速开始](../getting-started/quickstart.md)

## 🤝 获取帮助

如果遇到数据库问题：

1. 检查连接配置
2. 查看错误日志
3. 验证SQL语法
4. 联系技术支持
