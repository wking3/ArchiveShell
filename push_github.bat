@echo off
chcp 65001 >nul
echo ================================================
echo ArchiveShell - Push to GitHub
echo ================================================
echo.

if "%~1"=="" (
    echo Usage: push_github.bat ^<GitHub_Token^
    echo.
    echo Get token from: https://github.com/settings/tokens
    echo.
    pause
    exit /b 1
)

set "GIT_TOKEN=%~1"
set "GIT_PATH=C:\Program Files\Git\bin\git.exe"

cd /d "%~dp0"

echo 1. Initialize repository...
"%GIT_PATH%" init
"%GIT_PATH%" branch -M main

echo 2. Add files...
"%GIT_PATH%" add .

echo 3. Commit...
"%GIT_PATH%" commit -m "Initial release: ArchiveShell v1.0.0"

echo 4. Set remote...
"%GIT_PATH%" remote remove origin 2>nul
"%GIT_PATH%" remote add origin https://oauth2:%GIT_TOKEN%@github.com/wking3/ArchiveShell.git

echo 5. Push to GitHub...
"%GIT_PATH%" push -u origin main -f

if %errorLevel% neq 0 (
    echo.
    echo Push failed! Please check:
    echo 1. GitHub Token is correct
    echo 2. Repository exists: https://github.com/new
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================
echo Success!
echo https://github.com/wking3/ArchiveShell
echo ================================================
echo.
pause
