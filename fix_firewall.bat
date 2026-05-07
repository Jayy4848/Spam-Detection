@echo off
echo ========================================
echo   FIXING FIREWALL FOR MOBILE ACCESS
echo ========================================
echo.
echo This will allow your phone to connect to the app.
echo.
echo You need to run this as Administrator!
echo.
pause

echo.
echo Adding firewall rules...
echo.

REM Allow Node.js (Frontend - Port 3000)
netsh advfirewall firewall add rule name="TextGuard Frontend" dir=in action=allow protocol=TCP localport=3000
netsh advfirewall firewall add rule name="TextGuard Frontend Out" dir=out action=allow protocol=TCP localport=3000

REM Allow Python (Backend - Port 8000)
netsh advfirewall firewall add rule name="TextGuard Backend" dir=in action=allow protocol=TCP localport=8000
netsh advfirewall firewall add rule name="TextGuard Backend Out" dir=out action=allow protocol=TCP localport=8000

echo.
echo ========================================
echo   FIREWALL RULES ADDED!
echo ========================================
echo.
echo Your phone should now be able to connect.
echo.
echo Try opening on your phone:
echo   http://192.168.0.102:3000
echo.
pause
