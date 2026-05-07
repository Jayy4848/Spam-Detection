@echo off
title TextGuard - Quick Start

echo ========================================
echo    TEXTGUARD SMS SECURITY
echo ========================================
echo.
echo Starting automatic setup...
echo.
echo This will:
echo 1. Find your IP address
echo 2. Update Android app
echo 3. Build APK
echo 4. Start server
echo.
echo Press any key to continue...
pause >nul

REM Get IP address
echo.
echo Finding your IP address...
for /f "tokens=14" %%a in ('ipconfig ^| findstr /i "IPv4"') do set IP=%%a
echo Found: %IP%
echo.
echo Your phone will connect to: http://%IP%:8000/api
echo.
pause

REM Update Android app
echo.
echo Updating Android app configuration...
powershell -Command "(Get-Content 'android\app\src\main\java\com\textguard\sms\ApiClient.java') -replace 'http://[0-9.]+:8000/api', 'http://%IP%:8000/api' | Set-Content 'android\app\src\main\java\com\textguard\sms\ApiClient.java'"
echo Done!
echo.
pause

REM Build APK
echo.
echo Building Android APK (this takes 2-3 minutes)...
echo Please wait...
echo.
cd android
call gradlew.bat assembleDebug
cd ..

if exist "android\app\build\outputs\apk\debug\app-debug.apk" (
    echo.
    echo ========================================
    echo SUCCESS! APK built successfully!
    echo ========================================
    echo.
    echo APK Location: android\app\build\outputs\apk\debug\app-debug.apk
    echo.
    echo Next: Transfer this APK to your phone and install it
    echo.
    pause
) else (
    echo.
    echo ERROR: APK build failed!
    pause
    exit /b 1
)

REM Start server
echo.
echo ========================================
echo Starting Backend Server
echo ========================================
echo.
echo Server URL: http://%IP%:8000/api
echo.
echo IMPORTANT: Keep this window open!
echo.
pause

cd backend
call venv\Scripts\activate.bat
python manage.py runserver 0.0.0.0:8000
