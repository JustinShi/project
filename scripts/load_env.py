#!/usr/bin/env python3
"""
从 .env 文件加载环境变量
"""
import os
from pathlib import Path

def load_env_file(env_file_path: str = ".env"):
    """从 .env 文件加载环境变量"""
    env_path = Path(env_file_path)
    
    if not env_path.exists():
        print(f"⚠️ .env 文件不存在: {env_path}")
        print("💡 请复制 env.example 为 .env 并配置相应的值")
        return False
    
    print(f"📁 加载环境变量文件: {env_path}")
    
    loaded_vars = []
    with open(env_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            # 跳过空行和注释
            if not line or line.startswith('#'):
                continue
            
            # 解析 KEY=VALUE 格式
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # 移除引号
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                # 设置环境变量
                os.environ[key] = value
                loaded_vars.append((key, value))
            else:
                print(f"⚠️ 第 {line_num} 行格式错误: {line}")
    
    if loaded_vars:
        print(f"✅ 成功加载 {len(loaded_vars)} 个环境变量:")
        for key, value in loaded_vars:
            # 隐藏敏感信息
            if 'PASSWORD' in key.upper() or 'KEY' in key.upper():
                display_value = '*' * len(value)
            else:
                display_value = value
            print(f"   {key}={display_value}")
    else:
        print("ℹ️ 没有找到有效的环境变量")
    
    return True

def show_current_proxy_settings():
    """显示当前代理设置"""
    print("\n🔧 当前代理环境变量:")
    proxy_vars = [
        'HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy',
        'ALL_PROXY', 'all_proxy', 'SOCKS_PROXY', 'socks_proxy'
    ]
    
    found_proxy = False
    for var in proxy_vars:
        value = os.environ.get(var)
        if value:
            print(f"   {var}={value}")
            found_proxy = True
    
    if not found_proxy:
        print("   ❌ 未设置代理环境变量")

def main():
    """主函数"""
    print("🚀 环境变量加载器")
    print("=" * 50)
    
    # 加载 .env 文件
    load_env_file()
    
    # 显示当前代理设置
    show_current_proxy_settings()
    
    print("\n" + "=" * 50)
    print("✅ 环境变量加载完成")

if __name__ == "__main__":
    main()
