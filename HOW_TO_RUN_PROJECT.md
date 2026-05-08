# 🚀 How to Run the SMS Security Assistant Project

## Quick Start (5 Minutes)

### Prerequisites
- Python 3.11+ installed
- Node.js 18+ installed
- Git installed

---

## Step 1: Clone the Project (if not already done)

```bash
git clone <your-repo-url>
cd <project-folder>
```

---

## Step 2: Setup Backend (Django API)

### 2.1 Navigate to Backend
```bash
cd backend
```

### 2.2 Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2.3 Install Dependencies
```bash
pip install -r requirements.txt
```

### 2.4 Download NLTK Data (Required for ML)
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"
```

### 2.5 Run Database Migrations
```bash
python manage.py migrate
```

### 2.6 (Optional) Create Admin User
```bash
python manage.py createsuperuser
```

### 2.7 Start Backend Server
```bash
python manage.py runserver
```

✅ **Backend is now running at: http://localhost:8000**

Test it: Open http://localhost:8000/api/health/ in your browser

---

## Step 3: Setup Frontend (React)

### 3.1 Open New Terminal
Keep the backend running, open a **new terminal window**

### 3.2 Navigate to Frontend
```bash
cd frontend
```

### 3.3 Install Dependencies
```bash
npm install
```

### 3.4 Start Frontend Server
```bash
npm start
```

✅ **Frontend is now running at: http://localhost:3000**

Your browser should automatically open to http://localhost:3000

---

## 🎉 You're Done!

The application is now running:
- **Frontend**: http://localhost:3000 (User Interface)
- **Backend**: http://localhost:8000 (API Server)

---

## 📱 How to Use the App

### 1. Home Page
- Enter an SMS message in the text box
- Select language (English, Hindi, Marathi)
- Click "Analyze Message"
- View the detailed analysis results

### 2. Dashboard
- View statistics and analytics
- See all analyzed messages in a table
- Click the eye icon to view message details
- Click the trash icon to delete messages
- Use filters to sort by category or risk level

### 3. About Page
- Learn about the technology stack
- View model information and accuracy

---

## 🛠️ Troubleshooting

### Backend Issues

**Error: "No module named 'django'"**
```bash
# Make sure virtual environment is activated
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

**Error: "Port 8000 is already in use"**
```bash
# Kill the process using port 8000
# Windows
netstat -ano | findstr :8000
taskkill /PID <process-id> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9

# Or use a different port
python manage.py runserver 8001
```

**Error: "NLTK data not found"**
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"
```

**Error: "Database is locked"**
```bash
# Close all terminals running the backend
# Delete db.sqlite3 and run migrations again
rm db.sqlite3
python manage.py migrate
```

### Frontend Issues

**Error: "npm: command not found"**
- Install Node.js from https://nodejs.org/

**Error: "Port 3000 is already in use"**
```bash
# Kill the process using port 3000
# Windows
netstat -ano | findstr :3000
taskkill /PID <process-id> /F

# Mac/Linux
lsof -ti:3000 | xargs kill -9
```

**Error: "Module not found"**
```bash
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Error: "Cannot connect to backend"**
- Make sure backend is running on http://localhost:8000
- Check frontend/.env file has correct API URL
- Check browser console for CORS errors

---

## 🔄 Stopping the Application

### Stop Backend
1. Go to the terminal running the backend
2. Press `Ctrl + C`
3. Deactivate virtual environment: `deactivate`

### Stop Frontend
1. Go to the terminal running the frontend
2. Press `Ctrl + C`

---

## 📊 Testing the ML Models

### Check Model Accuracy
```bash
cd backend
python test_accuracy.py
```

### Train New Models (Optional)
```bash
cd backend
python train_models.py
```

This will:
- Train 5 different ML models
- Save the best model
- Generate accuracy reports

---

## 🗄️ Database Management

### View Database
```bash
cd backend
python manage.py dbshell
```

### Reset All Data
- Use the "Reset Data" button in the Dashboard
- Or manually: Delete `backend/db.sqlite3` and run migrations

### Create Backup
```bash
cd backend
cp db.sqlite3 db.sqlite3.backup
```

---

## 🎨 Development Tips

### Backend Development
```bash
# Run with auto-reload (default)
python manage.py runserver

# Run on different port
python manage.py runserver 8001

# Run on all interfaces (accessible from other devices)
python manage.py runserver 0.0.0.0:8000

# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Access admin panel
# http://localhost:8000/admin/
```

### Frontend Development
```bash
# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Lint code
npm run lint
```

---

## 📁 Project Structure

```
project/
├── backend/                 # Django API
│   ├── api/                # API endpoints
│   ├── ml_models/          # ML models and training
│   ├── sms_security/       # Django settings
│   ├── manage.py           # Django management
│   └── requirements.txt    # Python dependencies
│
├── frontend/               # React UI
│   ├── src/               # Source code
│   │   ├── components/    # React components
│   │   ├── services/      # API services
│   │   └── App.js         # Main app
│   ├── public/            # Static files
│   └── package.json       # Node dependencies
│
└── data/                  # Training data
    └── sample_sms_dataset.csv
```

---

## 🔐 Environment Variables

### Backend (.env)
Create `backend/.env` file:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Frontend (.env)
Already configured in `frontend/.env`:
```env
REACT_APP_API_URL=http://localhost:8000
```

---

## 📝 Common Commands Cheat Sheet

### Backend
```bash
cd backend
venv\Scripts\activate              # Activate virtual environment (Windows)
source venv/bin/activate           # Activate virtual environment (Mac/Linux)
python manage.py runserver         # Start server
python manage.py migrate           # Run migrations
python manage.py createsuperuser   # Create admin user
python test_accuracy.py            # Test model accuracy
python train_models.py             # Train new models
deactivate                         # Deactivate virtual environment
```

### Frontend
```bash
cd frontend
npm install                        # Install dependencies
npm start                          # Start development server
npm run build                      # Build for production
npm test                           # Run tests
```

---

## 🌐 Accessing from Other Devices

### On Same Network (Phone, Tablet, etc.)

1. **Find your computer's IP address**:
   ```bash
   # Windows
   ipconfig
   # Look for "IPv4 Address" (e.g., 192.168.1.100)
   
   # Mac/Linux
   ifconfig
   # Look for "inet" (e.g., 192.168.1.100)
   ```

2. **Start backend on all interfaces**:
   ```bash
   cd backend
   python manage.py runserver 0.0.0.0:8000
   ```

3. **Update frontend API URL**:
   Edit `frontend/.env`:
   ```env
   REACT_APP_API_URL=http://192.168.1.100:8000
   ```

4. **Start frontend**:
   ```bash
   cd frontend
   npm start
   ```

5. **Access from other device**:
   - Open browser on phone/tablet
   - Go to: `http://192.168.1.100:3000`

---

## 🚀 Production Deployment

See these guides:
- **Railway**: `RAILWAY_QUICK_SETUP.md`
- **Detailed Guide**: `RAILWAY_DEPLOYMENT_GUIDE.txt`

---

## 📞 Need Help?

### Check Logs
- **Backend**: Terminal running `python manage.py runserver`
- **Frontend**: Terminal running `npm start`
- **Browser**: Press F12 → Console tab

### Common Issues
1. Backend not starting → Check Python version, virtual environment
2. Frontend not starting → Check Node.js version, npm install
3. Can't analyze messages → Check backend is running, check browser console
4. CORS errors → Check CORS_ALLOWED_ORIGINS in backend settings

---

## ✅ Quick Verification

After starting both servers, verify everything works:

1. **Backend Health Check**:
   - Open: http://localhost:8000/api/health/
   - Should see: `{"status": "healthy", "message": "..."}`

2. **Frontend Loading**:
   - Open: http://localhost:3000
   - Should see: SMS Security Assistant interface

3. **Test Analysis**:
   - Enter message: "Congratulations! You won $1000"
   - Click "Analyze Message"
   - Should see: Spam classification with high confidence

---

## 🎯 Summary

**To run the project:**

1. **Terminal 1 (Backend)**:
   ```bash
   cd backend
   venv\Scripts\activate
   python manage.py runserver
   ```

2. **Terminal 2 (Frontend)**:
   ```bash
   cd frontend
   npm start
   ```

3. **Open Browser**:
   - Go to http://localhost:3000
   - Start analyzing messages!

---

**Status**: Ready to run! Follow the steps above. 🚀
