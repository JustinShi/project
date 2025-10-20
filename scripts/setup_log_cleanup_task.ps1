# PowerShell脚本：设置Windows任务计划，定期清理日志文件
# 使用方法：以管理员身份运行PowerShell，然后执行此脚本

param(
    [string]$ProjectPath = "C:\Users\JustinShi\Pyproject",
    [int]$RetentionDays = 7,
    [string]$TaskName = "BinanceTradingLogCleanup"
)

# 检查是否以管理员身份运行
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "此脚本需要管理员权限运行"
    exit 1
}

# 检查项目路径是否存在
if (-not (Test-Path $ProjectPath)) {
    Write-Error "项目路径不存在: $ProjectPath"
    exit 1
}

# 构建Python命令
$PythonCommand = "cd '$ProjectPath' && uv run python scripts/cleanup_logs.py --retention-days $RetentionDays"

# 创建任务计划
try {
    # 删除已存在的任务（如果存在）
    $existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($existingTask) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "已删除现有任务: $TaskName"
    }

    # 创建新的任务计划
    $action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$PythonCommand`""
    $trigger = New-ScheduledTaskTrigger -Daily -At "02:00"  # 每天凌晨2点执行
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "定期清理币安交易系统日志文件"

    Write-Host "✅ 任务计划创建成功！"
    Write-Host "任务名称: $TaskName"
    Write-Host "执行时间: 每天凌晨2:00"
    Write-Host "保留天数: $RetentionDays 天"
    Write-Host "项目路径: $ProjectPath"
    Write-Host ""
    Write-Host "查看任务计划:"
    Write-Host "Get-ScheduledTask -TaskName '$TaskName'"
    Write-Host ""
    Write-Host "手动执行任务:"
    Write-Host "Start-ScheduledTask -TaskName '$TaskName'"
    Write-Host ""
    Write-Host "删除任务计划:"
    Write-Host "Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"

} catch {
    Write-Error "创建任务计划失败: $($_.Exception.Message)"
    exit 1
}
