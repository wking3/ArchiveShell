@echo off
chcp 65001 >nul
echo ================================================
echo ArchiveShell - 一键打包 (简化版)
echo ================================================
echo.

REM 检查是否安装 PyInstaller
python -m pip show pyinstaller >nul 2>&1
if %errorLevel% neq 0 (
    echo 正在安装 PyInstaller...
    pip install pyinstaller
)

echo.
echo 正在打包主程序...
echo.

REM 使用 --onefile 参数打包成单个可执行文件
pyinstaller --onefile ^
    --name ArchiveBrowser ^
    --add-data "requirements.txt;." ^
    --add-data "README.md;." ^
    --hidden-import py7zr ^
    --hidden-import py7zr.helpers ^
    --hidden-import py7zr.compressor ^
    --hidden-import rarfile ^
    --hidden-import cryptography ^
    --hidden-import Cryptodome.Cipher ^
    --hidden-import Cryptodome.Util ^
    --hidden-import texttable ^
    --hidden-import multivolumefile ^
    --hidden-import pyzstd ^
    --hidden-import inflate64 ^
    --hidden-import bcj ^
    --console ^
    archive_handler.py

if %errorLevel% neq 0 (
    echo.
    echo 打包失败！
    pause
    exit /b 1
)

echo.
echo ================================================
echo 打包完成！
echo ================================================
echo.
echo 生成的文件：dist\ArchiveBrowser.exe
echo.

REM 测试文件是否存在
if exist "dist\ArchiveBrowser.exe" (
    dir /B dist\ArchiveBrowser.exe
    echo.
    echo 按任意键打开输出目录...
    pause >nul
    explorer dist
)

pause
