@echo off
echo ========================================
echo Smart SMS Security Assistant - Backend Setup
echo ========================================
echo.

cd backend

echo Creating virtual environment...
python -m venv venv

echo.
echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Running database migrations...
python manage.py makemigrations
python manage.py migrate

echo.
echo Training machine learning models...
echo You will be asked if you want to train BERT model.
echo For quick setup, choose 'n' to use only Naive Bayes.
echo.
python train_models.py

echo.
echo ========================================
echo Backend setup complete!
echo ========================================
echo.
echo To start the backend server, run: start_backend.bat
echo Or manually: cd backend, venv\Scripts\activate, python manage.py runserver
echo.
pause
