@echo off
color 0B
title TextGuard - Quick Start

cls
echo.
echo  ========================================
echo     TEXTGUARD SMS SECURITY - QUICK START
echo  ========================================
echo.
echo  This will automatically:
echo.
echo  [1] Find your computer's IP address
echo  [2] Configure the Android app
echo  [3] Build the APK file
echo  [4] Start the backend server
echo.
echo  ========================================
echo.
echo  Requirements:
echo  - Phone and computer on SAME WiFi
echo  - Android 6.0 or higher
echo.
echo  ========================================
echo.
echo  Press any key to start automatic setup...
echo  (or close this window to cancel)
echo.
pause >nul

call auto_setup.bat
