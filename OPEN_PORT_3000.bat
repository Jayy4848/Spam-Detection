@echo off
echo ========================================
echo   OPENING PORT 3000 FOR MOBILE ACCESS
echo ========================================
echo.
echo This will allow your phone to access the frontend.
echo.
echo Running as Administrator...
echo.

REM Add firewall rule for port 3000
netsh advfirewall firewall add rule name="TextGuard Frontend Port 3000 IN" dir=in action=allow protocol=TCP localport=3000

netsh advfirewall firewall add rule name="TextGuard Frontend Port 3000 OUT" dir=out action=allow protocol=TCP localport=3000

echo.
echo ========================================
echo   PORT 3000 IS NOW OPEN!
echo ========================================
echo.
echo Try accessing from your phone:
echo   http://192.168.0.102:3000
echo.
echo If it still doesn't work:
echo 1. Make sure both devices are on SAME WiFi
echo 2. Restart Chrome on your phone
echo 3. Clear Chrome cache
echo.
pause
