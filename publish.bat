@echo off
chcp 65001 >nul
echo ================================================
echo ArchiveShell - GitHub 发布工具
echo ================================================
echo.

REM 检查是否有 token 参数
if "%~1"=="" (
    echo 用法：publish.bat ^<GitHub_Token^ [版本号]
    echo.
    echo 或者设置环境变量:
    echo   set GITHUB_TOKEN=your_token
    echo   publish.bat [版本号]
    echo.
    pause
    exit /b 1
)

echo 正在发布到 GitHub...
python publish_github.py %*

if %errorLevel% neq 0 (
    echo.
    echo 发布失败！
    pause
    exit /b 1
)

echo.
pause
