# 🚀 How to Run TextGuard AI - SMS Security System

## 📋 Prerequisites

Before running the project, make sure you have:

- **Python 3.8+** installed
- **Node.js 14+** and npm installed
- **Git** (if cloning from repository)

---

## 🔧 Setup Instructions

### **Step 1: Install Backend Dependencies**

Open a terminal and navigate to the backend folder:

```bash
cd backend
```

**Option A: Using Virtual Environment (Recommended)**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Option B: Without Virtual Environment**
```bash
pip install -r requirements.txt
```

---

### **Step 2: Setup Database**

Run database migrations:

```bash
python manage.py migrate
```

Expected output:
```
Operations to perform:
  Apply all migrations: admin, api, auth, contenttypes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
```

---

### **Step 3: Train ML Models** (Already done, but if needed)

```bash
python train_models.py
```

This will:
- Load the dataset (286 samples)
- Train 10 model combinations
- Save the best model (96.55% accuracy)
- Takes ~2-3 minutes

---

### **Step 4: Start Backend Server**

```bash
python manage.py runserver
```

Expected output:
```
Django version 4.x.x, using settings 'sms_security.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

✅ **Backend is now running on http://localhost:8000**

**Keep this terminal open!**

---

### **Step 5: Install Frontend Dependencies**

Open a **NEW terminal** (keep backend running) and navigate to frontend:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

This will install React and all required packages (~2-3 minutes).

---

### **Step 6: Start Frontend Server**

```bash
npm start
```

Expected output:
```
Compiled successfully!

You can now view frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

✅ **Frontend is now running on http://localhost:3000**

Your browser should automatically open to http://localhost:3000

---

## 🎯 Quick Start (All-in-One)

### **Terminal 1: Backend**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### **Terminal 2: Frontend**
```bash
cd frontend
npm install
npm start
```

---

## 🌐 Accessing the Application

Once both servers are running:

1. **Frontend:** http://localhost:3000
2. **Backend API:** http://localhost:8000/api/

### **Available Pages:**

- **Home (Analyzer):** http://localhost:3000/
  - Analyze SMS messages
  - See real-time predictions
  - View model confidence scores

- **Dashboard:** http://localhost:3000/dashboard
  - View analytics and statistics
  - See message history
  - Monitor model performance
  - Delete messages

- **About:** http://localhost:3000/about
  - Learn about the system
  - View model information
  - See features

---

## 🧪 Testing the System

### **Test 1: Analyze a Spam Message**

1. Go to http://localhost:3000
2. Enter: `WINNER! You won $10000! Click now to claim!`
3. Click "Analyze Message"
4. Expected: **Category: Spam** (High confidence)

### **Test 2: Analyze an OTP**

1. Enter: `Your OTP is 123456. Valid for 10 minutes.`
2. Click "Analyze Message"
3. Expected: **Category: OTP** (High confidence)

### **Test 3: View Dashboard**

1. Go to http://localhost:3000/dashboard
2. You should see:
   - Total messages analyzed
   - Spam detection rate
   - Model accuracy: **96.55%**
   - Message history table

---

## 🔍 Troubleshooting

### **Problem: Backend won't start**

**Error:** `Port 8000 is already in use`

**Solution:**
```bash
# Windows - Find and kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F

# Then restart
python manage.py runserver
```

---

### **Problem: Frontend won't start**

**Error:** `Port 3000 is already in use`

**Solution:**
```bash
# Kill process on port 3000
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID_NUMBER> /F

# Or use a different port:
set PORT=3001 && npm start
```

---

### **Problem: "Cannot reach server" error**

**Cause:** Backend is not running

**Solution:**
1. Check if backend terminal is still running
2. Restart backend: `python manage.py runserver`
3. Refresh frontend (Ctrl+Shift+R)

---

### **Problem: "Module not found" errors**

**Backend:**
```bash
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

---

### **Problem: Database errors**

**Solution:**
```bash
cd backend
python manage.py migrate
```

If still having issues:
```bash
# Delete database and recreate
del db.sqlite3  # Windows
rm db.sqlite3   # Mac/Linux

# Recreate
python manage.py migrate
python train_models.py
```

---

## 📱 Running on Mobile/Other Devices

### **Access from Phone (Same WiFi)**

1. Find your computer's IP address:
   ```bash
   # Windows
   ipconfig
   # Look for "IPv4 Address" (e.g., 192.168.1.100)
   
   # Mac/Linux
   ifconfig
   ```

2. On your phone's browser, go to:
   - Frontend: `http://192.168.1.100:3000`
   - Backend: `http://192.168.1.100:8000`

3. Make sure both devices are on the same WiFi network

---

## 🛑 Stopping the Servers

### **Stop Backend:**
- Press `Ctrl+C` in the backend terminal

### **Stop Frontend:**
- Press `Ctrl+C` in the frontend terminal

### **Deactivate Virtual Environment:**
```bash
deactivate
```

---

## 📊 Project Structure

```
Project Root/
├── backend/                 # Django Backend
│   ├── api/                # API endpoints
│   ├── ml_models/          # ML models and training
│   │   └── trained_models/ # Saved models (96.55% accuracy)
│   ├── manage.py           # Django management
│   ├── requirements.txt    # Python dependencies
│   └── train_models.py     # Model training script
│
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   └── services/      # API services
│   ├── package.json       # Node dependencies
│   └── public/            # Static files
│
└── data/                  # Training dataset
    └── sample_sms_dataset.csv  # 286 SMS samples
```

---

## 🔑 Key Features

✅ **Real-time SMS Analysis**
- Instant classification (spam, promotion, OTP, important, personal)
- 96.55% accuracy
- Confidence scores

✅ **Advanced ML Models**
- 5 different algorithms
- Ensemble voting
- TF-IDF vectorization

✅ **Professional Dashboard**
- Analytics and statistics
- Message history
- Model performance metrics
- Delete functionality

✅ **Responsive Design**
- Works on desktop, tablet, mobile
- Glassmorphism UI
- Dark mode toggle

---

## 📝 Common Commands

### **Backend Commands:**
```bash
# Start server
python manage.py runserver

# Run migrations
python manage.py migrate

# Train models
python train_models.py

# Check accuracy
python test_accuracy.py

# Create superuser (admin)
python manage.py createsuperuser
```

### **Frontend Commands:**
```bash
# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test
```

---

## 🎓 First Time Setup (Complete)

```bash
# 1. Clone/Download project
cd "D:\Jayy\ME\Project\Spam Detection"

# 2. Setup Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python train_models.py

# 3. Setup Frontend (new terminal)
cd frontend
npm install

# 4. Run Backend (terminal 1)
cd backend
venv\Scripts\activate
python manage.py runserver

# 5. Run Frontend (terminal 2)
cd frontend
npm start

# 6. Open browser
# http://localhost:3000
```

---

## ✅ Success Checklist

- [ ] Python 3.8+ installed
- [ ] Node.js 14+ installed
- [ ] Backend dependencies installed
- [ ] Database migrated
- [ ] ML models trained (96.55% accuracy)
- [ ] Backend running on port 8000
- [ ] Frontend dependencies installed
- [ ] Frontend running on port 3000
- [ ] Browser opens to http://localhost:3000
- [ ] Can analyze SMS messages
- [ ] Dashboard shows statistics

---

## 🆘 Need Help?

### **Check Backend Status:**
```bash
curl http://localhost:8000/api/health/
```
Should return: `{"status": "healthy"}`

### **Check Frontend Status:**
Open: http://localhost:3000
Should show the TextGuard AI homepage

### **View Backend Logs:**
Check the terminal where backend is running for error messages

### **View Frontend Logs:**
Press F12 in browser → Console tab

---

## 🎉 You're All Set!

Your TextGuard AI SMS Security System is now running with:
- ✅ 96.55% accuracy
- ✅ 5 ML models
- ✅ Real-time analysis
- ✅ Professional dashboard
- ✅ Responsive design

**Enjoy analyzing SMS messages!** 🚀
