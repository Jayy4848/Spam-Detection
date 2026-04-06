@echo off
echo ========================================
echo Smart SMS Security Assistant - Backend
echo ========================================
echo.

cd backend

echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Starting Django server...
echo Backend will be available at: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.

python manage.py runserver
