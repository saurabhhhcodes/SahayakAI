@echo off
set "GIT_PATH=C:\Program Files\Git\cmd\git.exe"

echo SahayakAI GitHub Push Helper
echo ============================
echo.

if not exist "%GIT_PATH%" (
    echo Error: Git not found at expected path: C:\Program Files\Git\cmd\git.exe
    echo Please verify Git installation.
    pause
    exit /b 1
)

echo Pushing to remote: https://github.com/adilakhatoon83-rgb/SahayakAI.git
echo.
echo NOTE: You may be asked to sign in to GitHub in the browser or terminal.
echo.

"%GIT_PATH%" push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Push successful!
) else (
    echo.
    echo Push failed. Please check the error message above.
)

pause
