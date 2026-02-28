@echo off
chcp 65001 >nul
echo ================================================
echo ArchiveShell - 打包成单文件可执行程序
echo ================================================
echo.

REM 检查是否安装 PyInstaller
python -m pip show pyinstaller >nul 2>&1
if %errorLevel% neq 0 (
    echo 正在安装 PyInstaller...
    pip install pyinstaller
)

echo.
echo [1/3] 打包主程序 (ArchiveBrowser.exe)...
pyinstaller --clean ArchiveBrowser.spec
if %errorLevel% neq 0 (
    echo 主程序打包失败！
    pause
    exit /b 1
)

echo.
echo [2/3] 打包安装程序 (ArchiveShellInstaller.exe)...
pyinstaller --clean ArchiveShellInstaller.spec
if %errorLevel% neq 0 (
    echo 安装程序打包失败！
    pause
    exit /b 1
)

echo.
echo [3/3] 创建发布包...
set DIST_DIR=dist\release
if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%"
mkdir "%DIST_DIR%"

REM 复制可执行文件
copy dist\ArchiveBrowser.exe "%DIST_DIR%\"
copy dist\ArchiveShellInstaller.exe "%DIST_DIR%\"

REM 复制说明文件
copy README.md "%DIST_DIR%\"

REM 创建快速安装脚本
(
echo @echo off
echo chcp 65001 ^>nul
echo echo ================================================
echo echo ArchiveShell - 快速安装
echo echo ================================================
echo echo.
echo echo 正在解压文件...
echo.
echo ArchiveBrowser.exe - 压缩文件浏览器
echo ArchiveShellInstaller.exe - 安装/卸载程序
echo.
echo ================================================
echo.
echo 使用方法:
echo   1. 以管理员身份运行：ArchiveShellInstaller.exe install
echo   2. 双击压缩文件即可浏览
echo.
echo 卸载方法:
echo   ArchiveShellInstaller.exe uninstall
echo.
echo pause
) > "%DIST_DIR%\快速使用说明.txt"

echo.
echo ================================================
echo 打包完成！
echo ================================================
echo.
echo 发布目录：%DIST_DIR%
echo.
echo 生成的文件:
echo   - ArchiveBrowser.exe         (压缩文件浏览器)
echo   - ArchiveShellInstaller.exe  (安装/卸载程序)
echo   - README.md                  (说明文档)
echo   - 快速使用说明.txt           (快速指南)
echo.

REM 打开发布目录
explorer "%DIST_DIR%"

pause
