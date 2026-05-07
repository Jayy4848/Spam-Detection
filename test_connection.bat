@echo off
echo ========================================
echo   CONNECTION TEST
echo ========================================
echo.
echo Your Computer's IP: 192.168.0.102
echo.
echo Testing if ports are open...
echo.

netstat -an | findstr ":3000"
netstat -an | findstr ":8000"

echo.
echo ========================================
echo   TROUBLESHOOTING STEPS
echo ========================================
echo.
echo 1. Make sure your phone is on the SAME WiFi network
echo    - Not mobile data
echo    - Not guest WiFi
echo    - Same network as computer
echo.
echo 2. Check Windows Firewall:
echo    - Run fix_firewall.bat as Administrator
echo.
echo 3. Try these URLs on your phone:
echo    - http://192.168.0.102:3000 (Frontend)
echo    - http://192.168.0.102:8000/api/health/ (Backend)
echo.
echo 4. If still not working:
echo    - Restart both servers
echo    - Check router settings (AP Isolation should be OFF)
echo.
pause
