# Netlify Deployment Guide - SMS Security Assistant

## Overview

This project uses a **split deployment strategy**:
- **Frontend (React)**: Deploy to Netlify ✅
- **Backend (Django)**: Deploy to Heroku, Railway, Render, or AWS ⚠️

Netlify only supports static sites and serverless functions, so the Django backend must be hosted elsewhere.

---

## Architecture

```
┌─────────────────┐
│   Netlify       │
│   (Frontend)    │
│   React App     │
└────────┬────────┘
         │
         │ HTTPS API Calls
         │
         ▼
┌─────────────────┐
│   Heroku/       │
│   Railway/      │
│   Render        │
│   (Backend)     │
│   Django API    │
└─────────────────┘
```

---

## Part 1: Deploy Frontend to Netlify

### Option A: Deploy via Netlify UI (Recommended)

#### Step 1: Prepare Repository
```bash
# Commit all changes
git add .
git commit -m "Prepare for Netlify deployment"
git push origin main
```

#### Step 2: Connect to Netlify
1. Go to [Netlify](https://app.netlify.com/)
2. Click "Add new site" → "Import an existing project"
3. Connect your Git provider (GitHub, GitLab, Bitbucket)
4. Select your repository
5. Configure build settings:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/build`

#### Step 3: Set Environment Variables
In Netlify dashboard → Site settings → Environment variables:
```
REACT_APP_API_URL = https://your-backend-url.herokuapp.com/api
NODE_VERSION = 18
```

#### Step 4: Deploy
Click "Deploy site" - Netlify will automatically build and deploy!

### Option B: Deploy via Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Navigate to frontend
cd frontend

# Build the project
npm run build

# Deploy
netlify deploy --prod
```

---

## Part 2: Deploy Backend (Choose One)

### Option 1: Heroku (Easiest)

#### Step 1: Create Heroku Account
Sign up at [heroku.com](https://heroku.com)

#### Step 2: Install Heroku CLI
```bash
# Windows
winget install Heroku.HerokuCLI

# macOS
brew tap heroku/brew && brew install heroku

# Linux
curl https://cli-assets.heroku.com/install.sh | sh
```

#### Step 3: Prepare Backend
```bash
cd backend

# Create Procfile
echo "web: gunicorn sms_security.wsgi --log-file -" > Procfile

# Create runtime.txt
echo "python-3.10.12" > runtime.txt

# Update requirements.txt
pip freeze > requirements.txt
```

#### Step 4: Deploy to Heroku
```bash
# Login
heroku login

# Create app
heroku create your-sms-backend

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set DEBUG=False
heroku config:set DJANGO_SECRET_KEY=your-secret-key-here
heroku config:set ALLOWED_HOSTS=your-sms-backend.herokuapp.com

# Deploy
git init
git add .
git commit -m "Deploy to Heroku"
heroku git:remote -a your-sms-backend
git push heroku main

# Run migrations
heroku run python manage.py migrate

# Create superuser (optional)
heroku run python manage.py createsuperuser
```

#### Step 5: Update Frontend Environment Variable
In Netlify dashboard, update:
```
REACT_APP_API_URL = https://your-sms-backend.herokuapp.com/api
```

### Option 2: Railway (Modern Alternative)

#### Step 1: Sign up at [railway.app](https://railway.app)

#### Step 2: Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your repository
4. Railway auto-detects Django

#### Step 3: Configure
1. Add PostgreSQL database (click "New" → "Database" → "PostgreSQL")
2. Set environment variables:
```
DEBUG=False
DJANGO_SECRET_KEY=your-secret-key
ALLOWED_HOSTS=your-app.railway.app
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

#### Step 4: Deploy
Railway automatically deploys on git push!

### Option 3: Render (Free Tier Available)

#### Step 1: Sign up at [render.com](https://render.com)

#### Step 2: Create Web Service
1. Click "New" → "Web Service"
2. Connect repository
3. Configure:
   - **Name**: sms-backend
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn sms_security.wsgi:application`

#### Step 3: Add PostgreSQL
1. Click "New" → "PostgreSQL"
2. Connect to web service

#### Step 4: Set Environment Variables
```
DEBUG=False
DJANGO_SECRET_KEY=your-secret-key
ALLOWED_HOSTS=your-app.onrender.com
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

---

## Part 3: Backend Configuration for Production

### Update Django Settings

Create `backend/sms_security/production_settings.py`:

```python
from .settings import *
import dj_database_url

DEBUG = False

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Database
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600
    )
}

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# CORS
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
```

### Install Additional Dependencies

```bash
pip install gunicorn dj-database-url whitenoise psycopg2-binary
pip freeze > requirements.txt
```

### Update requirements.txt

Add these lines:
```
gunicorn==21.2.0
dj-database-url==2.1.0
whitenoise==6.6.0
psycopg2-binary==2.9.9
```

---

## Part 4: CORS Configuration

### Update Backend CORS Settings

In `backend/sms_security/settings.py`:

```python
# CORS Settings for Production
CORS_ALLOWED_ORIGINS = [
    'https://your-app.netlify.app',
    'http://localhost:3000',  # For development
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnn-custom-header',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
```

---

## Part 5: Testing Deployment

### Test Frontend
```bash
# Visit your Netlify URL
https://your-app.netlify.app

# Check console for errors
# Verify API calls are going to correct backend URL
```

### Test Backend
```bash
# Health check
curl https://your-backend.herokuapp.com/api/health/

# Test prediction
curl -X POST https://your-backend.herokuapp.com/api/predict/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Test message", "language": "en"}'
```

### Test Integration
1. Open frontend in browser
2. Enter a test message
3. Click "Analyze Message"
4. Verify results appear correctly

---

## Part 6: Custom Domain (Optional)

### For Netlify (Frontend)
1. Go to Site settings → Domain management
2. Click "Add custom domain"
3. Follow DNS configuration instructions

### For Heroku (Backend)
```bash
heroku domains:add api.yourdomain.com
```

Then add CNAME record in your DNS:
```
api.yourdomain.com → your-app.herokuapp.com
```

---

## Deployment Checklist

### Frontend (Netlify)
- [ ] Repository connected to Netlify
- [ ] Build settings configured
- [ ] Environment variables set
- [ ] `netlify.toml` file present
- [ ] Successful build and deploy
- [ ] Site accessible via Netlify URL

### Backend (Heroku/Railway/Render)
- [ ] Backend deployed successfully
- [ ] Database connected
- [ ] Migrations run
- [ ] Environment variables set
- [ ] Static files configured
- [ ] CORS configured correctly
- [ ] API endpoints accessible

### Integration
- [ ] Frontend can reach backend API
- [ ] CORS working correctly
- [ ] Predictions working
- [ ] No console errors
- [ ] SSL/HTTPS working

---

## Cost Estimates

### Free Tier Options:

| Service | Frontend | Backend | Database | Limits |
|---------|----------|---------|----------|--------|
| **Netlify** | ✅ Free | ❌ N/A | ❌ N/A | 100GB bandwidth/month |
| **Heroku** | ❌ N/A | ⚠️ $7/mo | ⚠️ $5/mo | 550 dyno hours/month (free tier deprecated) |
| **Railway** | ❌ N/A | ✅ $5 credit | ✅ Included | $5/month free credit |
| **Render** | ❌ N/A | ✅ Free | ✅ Free | 750 hours/month |

### Recommended Setup (Free):
- **Frontend**: Netlify (Free)
- **Backend**: Render (Free tier)
- **Database**: Render PostgreSQL (Free tier)
- **Total Cost**: $0/month

### Recommended Setup (Production):
- **Frontend**: Netlify Pro ($19/month)
- **Backend**: Heroku Standard ($25/month)
- **Database**: Heroku PostgreSQL ($9/month)
- **Total Cost**: $53/month

---

## Alternative: Serverless Deployment

### Option: Vercel + Serverless Functions

If you want everything on one platform, consider rewriting the backend as serverless functions:

1. **Convert Django views to Vercel serverless functions**
2. **Use Vercel's built-in PostgreSQL**
3. **Deploy both frontend and backend to Vercel**

This requires significant refactoring but keeps everything in one place.

---

## Troubleshooting

### Issue: CORS Errors
**Solution**: Ensure backend CORS settings include your Netlify URL

### Issue: API Not Reachable
**Solution**: Check `REACT_APP_API_URL` environment variable in Netlify

### Issue: Database Connection Error
**Solution**: Verify `DATABASE_URL` is set correctly in backend

### Issue: Static Files Not Loading
**Solution**: Run `python manage.py collectstatic` and configure WhiteNoise

### Issue: Build Fails on Netlify
**Solution**: Check Node version, ensure `package.json` is correct

---

## Summary

### ✅ Netlify-Friendly Components:
- React frontend
- Static assets
- Client-side routing

### ❌ NOT Netlify-Friendly:
- Django backend
- Python ML models
- Database operations
- Server-side processing

### 🎯 Recommended Approach:
1. **Frontend**: Deploy to Netlify (Free)
2. **Backend**: Deploy to Render (Free) or Heroku ($7/mo)
3. **Database**: Use platform's PostgreSQL
4. **Total Setup Time**: 30-60 minutes

---

## Quick Start Commands

```bash
# Frontend to Netlify
cd frontend
npm run build
netlify deploy --prod

# Backend to Heroku
cd backend
heroku create
git push heroku main
heroku run python manage.py migrate

# Update frontend with backend URL
# In Netlify: Set REACT_APP_API_URL environment variable
```

---

**Your project IS Netlify-friendly for the frontend!**
**Backend needs separate hosting (Heroku/Railway/Render)**

This is the standard approach for full-stack applications and is actually better for scalability and separation of concerns.

---

**Last Updated**: April 6, 2026
**Status**: Production Deployment Ready 🚀
