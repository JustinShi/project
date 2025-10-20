@echo off
REM 批处理文件：设置Windows任务计划，定期清理日志文件
REM 需要管理员权限运行

echo ========================================
echo 币安交易系统 - 日志清理任务设置
echo ========================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ 检测到管理员权限
) else (
    echo ❌ 需要管理员权限运行此脚本
    echo 请右键点击此文件，选择"以管理员身份运行"
    pause
    exit /b 1
)

echo.
echo 正在设置日志清理任务计划...
echo.

REM 执行PowerShell脚本
powershell.exe -ExecutionPolicy Bypass -File "%~dp0setup_log_cleanup_task.ps1"

echo.
echo 设置完成！
echo.
pause
