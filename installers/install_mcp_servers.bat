@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo MCP服务器自动安装工具
echo ==============================
echo.

REM 检查npm是否安装
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误: 未检测到npm，请先安装Node.js和npm
    echo 访问 https://nodejs.org/ 下载并安装Node.js
    pause
    exit /b 1
)

REM 检查清单文件是否存在
if not exist "mcp_server_lists.txt" (
    echo 错误: 清单文件 mcp_server_lists.txt 不存在
    pause
    exit /b 1
)

REM 读取服务器清单
set "server_count=0"
set "success_count=0"
set "fail_count=0"

for /f "usebackq delims=" %%i in ("mcp_server_lists.txt") do (
    set "line=%%i"
    set "line=!line:#=!"
    if not "!line!"=="" (
        if "!line:~0,1!" neq "#" (
            set /a server_count+=1
            set "server_!server_count!=!line!"
        )
    )
)

if !server_count! equ 0 (
    echo 未找到需要安装的MCP服务器
    pause
    exit /b 0
)

echo 发现 !server_count! 个MCP服务器需要安装
echo.

REM 逐个安装服务器
for /l %%i in (1,1,!server_count!) do (
    set "current_server=!server_%%i!"
    echo [%%i/!server_count!] 正在安装 !current_server!...
    
    REM 使用npm安装
    npm install -g !current_server! >nul 2>&1
    
    if !errorlevel! equ 0 (
        echo ✓ !current_server! 安装成功
        set /a success_count+=1
    ) else (
        echo ✗ !current_server! 安装失败
        set /a fail_count+=1
    )
    echo.
)

REM 输出安装报告
echo ==============================
echo 安装完成报告:
echo 成功: !success_count! 个
echo 失败: !fail_count! 个
echo 总计: !server_count! 个

if !fail_count! gtr 0 (
    echo.
    echo 有 !fail_count! 个服务器安装失败，请检查网络连接和npm配置
    pause
    exit /b 1
) else (
    echo.
    echo 所有MCP服务器安装成功！
    pause
)

endlocal