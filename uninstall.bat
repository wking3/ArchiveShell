@echo off
chcp 65001 >nul
echo ================================================
echo ArchiveShell - 卸载程序
echo ================================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo 需要管理员权限...
    powershell -Command "Start-Process cmd -ArgumentList '/c', '%~f0' -Verb RunAs"
    exit /b
)

echo 正在注销 Shell 扩展...
python register.py uninstall

echo.
echo ================================================
echo 卸载完成！
echo ================================================
echo.
pause
