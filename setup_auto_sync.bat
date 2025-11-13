@echo off
echo ========================================
echo AI项目规则自动同步设置
echo ========================================

REM 检查Python是否可用
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Python未安装或不在PATH中
    echo 请先安装Python并确保其在系统PATH中
    pause
    exit /b 1
)

REM 安装必要的Python包
echo 正在检查并安装必要的Python包...
pip install schedule >nul 2>&1
if %errorlevel% neq 0 (
    echo 警告: 无法自动安装schedule包，但脚本仍可运行
)

REM 检查当前目录
set REPO_PATH=%~dp0
cd /d "%REPO_PATH%"

REM 检查Git仓库状态
git status >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 当前目录不是Git仓库或Git未安装
    echo 请先初始化Git仓库并配置远程仓库
    pause
    exit /b 1
)

REM 检查远程仓库
git remote -v | findstr "origin" >nul
if %errorlevel% neq 0 (
    echo 错误: 未配置远程仓库
    echo 请先配置远程仓库: git remote add origin <仓库URL>
    pause
    exit /b 1
)

echo.
echo 正在设置自动同步...

REM 创建Windows任务计划程序
echo 创建Windows任务计划...

REM 删除已存在的任务（如果存在）
schtasks /delete /tn "AI_Rules_Auto_Sync" /f >nul 2>&1

REM 创建新的任务计划
set TASK_NAME=AI_Rules_Auto_Sync
set SCRIPT_PATH=%REPO_PATH%auto_sync.py
set PYTHON_PATH=%~dp0..\..\..\python.exe

REM 如果找不到Python，使用系统Python
if not exist "%PYTHON_PATH%" (
    set PYTHON_PATH=python
)

REM 创建XML任务定义
echo ^<Task xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task"^> > task.xml
echo   ^<RegistrationInfo^> >> task.xml
echo     ^<Date^>%date% %time%^</Date^> >> task.xml
echo     ^<Author^>AI Project Rules^</Author^> >> task.xml
echo     ^<Description^>每72小时自动同步AI项目规则到GitHub^</Description^> >> task.xml
echo   ^</RegistrationInfo^> >> task.xml
echo   ^<Triggers^> >> task.xml
echo     ^<CalendarTrigger^> >> task.xml
echo       ^<StartBoundary^>%date%T%time%^</StartBoundary^> >> task.xml
echo       ^<ScheduleByDay^> >> task.xml
echo         ^<DaysInterval^>3^</DaysInterval^> >> task.xml
echo       ^</ScheduleByDay^> >> task.xml
echo     ^</CalendarTrigger^> >> task.xml
echo   ^</Triggers^> >> task.xml
echo   ^<Principals^> >> task.xml
echo     ^<Principal id="Author"^> >> task.xml
echo       ^<LogonType^>InteractiveToken^</LogonType^> >> task.xml
echo       ^<UserId^>%USERNAME%^</UserId^> >> task.xml
echo     ^</Principal^> >> task.xml
echo   ^</Principals^> >> task.xml
echo   ^<Settings^> >> task.xml
echo     ^<Enabled^>true^</Enabled^> >> task.xml
echo     ^<Hidden^>false^</Hidden^> >> task.xml
echo     ^<RunOnlyIfIdle^>false^</RunOnlyIfIdle^> >> task.xml
echo     ^<WakeToRun^>true^</WakeToRun^> >> task.xml
echo     ^<ExecutionTimeLimit^>PT1H^</ExecutionTimeLimit^> >> task.xml
echo     ^<Priority^>6^</Priority^> >> task.xml
echo   ^</Settings^> >> task.xml
echo   ^<Actions Context="Author"^> >> task.xml
echo     ^<Exec^> >> task.xml
echo       ^<Command^>%PYTHON_PATH%^</Command^> >> task.xml
echo       ^<Arguments^>"%SCRIPT_PATH%" sync^</Arguments^> >> task.xml
echo       ^<WorkingDirectory^>%REPO_PATH%^</WorkingDirectory^> >> task.xml
echo     ^</Exec^> >> task.xml
echo   ^</Actions^> >> task.xml
echo ^</Task^> >> task.xml

REM 导入任务
echo 正在创建任务计划...
schtasks /create /tn "%TASK_NAME%" /xml task.xml /f
if %errorlevel% neq 0 (
    echo 警告: 无法创建任务计划，但可以使用手动方式运行
    del task.xml
) else (
    echo 成功创建任务计划: %TASK_NAME%
    del task.xml
)

REM 创建快捷方式
echo.
echo 创建快捷方式...
echo @echo off ^> run_sync.bat
echo cd /d "%REPO_PATH%" ^>^> run_sync.bat
echo python auto_sync.py sync ^>^> run_sync.bat
echo pause ^>^> run_sync.bat

echo @echo off ^> check_status.bat
echo cd /d "%REPO_PATH%" ^>^> check_status.bat
echo python auto_sync.py status ^>^> check_status.bat
echo pause ^>^> check_status.bat

echo @echo off ^> stop_sync.bat
echo cd /d "%REPO_PATH%" ^>^> stop_sync.bat
echo python auto_sync.py stop ^>^> stop_sync.bat
echo echo 已停止自动同步调度器 ^>^> stop_sync.bat
echo pause ^>^> stop_sync.bat

echo.
echo ========================================
echo 自动同步设置完成！
echo ========================================
echo.
echo 使用方法:
echo   1. 手动同步: 双击 run_sync.bat
echo   2. 查看状态: 双击 check_status.bat  
echo   3. 停止同步: 双击 stop_sync.bat
echo.
echo 自动同步:
echo   - 每72小时自动同步一次
echo   - 自动提交本地更改
echo   - 自动推送到远程仓库
echo.
echo 日志文件:
echo   - auto_sync.log: 同步日志
echo   - rule_update.log: 规则更新日志
echo.
echo 配置文件:
echo   - sync_config.json: 同步配置
echo   - rule_config.json: 规则配置
echo.
echo ========================================
echo 设置完成！按任意键退出...
pause >nul