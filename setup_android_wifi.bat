@echo off
echo ========================================
echo TextGuard Android - WiFi Setup
echo ========================================
echo.

echo STEP 1: Finding your computer's IP address...
echo.
ipconfig | findstr /i "IPv4"
echo.
echo Copy one of the IPv4 addresses above (e.g., 192.168.1.5)
echo.

echo ========================================
echo STEP 2: Update the Android app
echo ========================================
echo.
echo 1. Open: android/app/src/main/java/com/textguard/sms/ApiClient.java
echo 2. Find line: this.baseUrl = prefs.getString("api_url", "http://192.168.1.5:8000/api");
echo 3. Replace 192.168.1.5 with YOUR IP address from above
echo 4. Save the file
echo.
pause

echo ========================================
echo STEP 3: Build the APK
echo ========================================
echo.
echo Building Android APK...
cd android
call gradlew assembleDebug
echo.
echo APK created at: android\app\build\outputs\apk\debug\app-debug.apk
echo.
pause

echo ========================================
echo STEP 4: Start Backend Server
echo ========================================
echo.
echo Starting backend server...
cd ..\backend
call venv\Scripts\activate
echo.
echo Server will start on: http://0.0.0.0:8000
echo Your phone should connect to: http://YOUR-IP:8000/api
echo.
echo Keep this window open!
echo.
python manage.py runserver 0.0.0.0:8000
