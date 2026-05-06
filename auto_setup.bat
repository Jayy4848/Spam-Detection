@echo off
color 0A
title TextGuard - Automatic Setup

echo ========================================
echo    TEXTGUARD - AUTOMATIC SETUP
echo ========================================
echo.
echo This script will:
echo 1. Find your IP address
echo 2. Update Android app configuration
echo 3. Build the APK
echo 4. Start the backend server
echo.
echo Press any key to start...
pause >nul
cls

echo ========================================
echo STEP 1: Finding Your IP Address
echo ========================================
echo.

REM Get IP address
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set IP=%%a
    goto :found
)
:found
set IP=%IP:~1%
echo Found IP Address: %IP%
echo.
echo Your phone should connect to: http://%IP%:8000/api
echo.
pause

cls
echo ========================================
echo STEP 2: Updating Android App
echo ========================================
echo.
echo Updating API URL in Android app to: http://%IP%:8000/api
echo.

REM Update ApiClient.java
powershell -Command "(Get-Content 'android\app\src\main\java\com\textguard\sms\ApiClient.java') -replace 'http://192.168.1.5:8000/api', 'http://%IP%:8000/api' | Set-Content 'android\app\src\main\java\com\textguard\sms\ApiClient.java'"

echo Done!
echo.
pause

cls
echo ========================================
echo STEP 3: Building Android APK
echo ========================================
echo.
echo This will take 2-3 minutes...
echo Please wait...
echo.

cd android
call gradlew.bat assembleDebug

if exist "app\build\outputs\apk\debug\app-debug.apk" (
    echo.
    echo ========================================
    echo SUCCESS! APK Built Successfully
    echo ========================================
    echo.
    echo APK Location: android\app\build\outputs\apk\debug\app-debug.apk
    echo.
    echo Next steps:
    echo 1. Transfer app-debug.apk to your phone
    echo 2. Install it on your phone
    echo 3. The backend server will start automatically
    echo.
    pause
) else (
    echo.
    echo ERROR: APK build failed!
    echo Please check the error messages above.
    echo.
    pause
    exit /b 1
)

cd ..

cls
echo ========================================
echo STEP 4: Starting Backend Server
echo ========================================
echo.
echo Server will start on: http://0.0.0.0:8000
echo Your phone should connect to: http://%IP%:8000/api
echo.
echo IMPORTANT: Keep this window open!
echo.
echo Press any key to start the server...
pause >nul

cd backend
call venv\Scripts\activate.bat
python manage.py runserver 0.0.0.0:8000
