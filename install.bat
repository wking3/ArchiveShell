@echo off
chcp 65001 >nul
echo ================================================
echo ArchiveShell - 安装程序
echo ================================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo 需要管理员权限...
    powershell -Command "Start-Process cmd -ArgumentList '/c', '%~f0' -Verb RunAs"
    exit /b
)

echo [1/3] 安装 Python 依赖...
pip install -r requirements.txt
if %errorLevel% neq 0 (
    echo 依赖安装失败！
    pause
    exit /b 1
)

echo.
echo [2/3] 注册 Shell 扩展...
python register.py install
if %errorLevel% neq 0 (
    echo 注册失败！
    pause
    exit /b 1
)

echo.
echo [3/3] 完成！
echo.
echo ================================================
echo 安装完成！
echo ================================================
echo.
echo 现在您可以：
echo   1. 双击 7z/RAR 文件直接浏览内容
echo   2. 右键点击压缩文件选择"浏览压缩包"
echo.
echo 如需卸载，请运行：
echo   python register.py uninstall
echo.
pause
