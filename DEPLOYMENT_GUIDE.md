# SMS Security Assistant - Deployment Guide

## Professional Deployment for Master's Level Project

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Development Setup](#development-setup)
3. [Training Models](#training-models)
4. [Running the Application](#running-the-application)
5. [Production Deployment](#production-deployment)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements:
- **OS**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Python**: 3.10 or higher
- **Node.js**: 16.x or higher
- **RAM**: Minimum 8GB (16GB recommended)
- **Disk Space**: 5GB free space

### Software Dependencies:
- Git
- Python pip
- Node.js npm
- Virtual environment tool (venv or conda)

---

## Development Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd sms-security-assistant
```

### 2. Backend Setup

#### Create Virtual Environment:
```bash
cd backend
python -m venv venv
```

#### Activate Virtual Environment:
**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

#### Install Dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Download NLTK Data:
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

#### Setup Database:
```bash
python manage.py makemigrations
python manage.py migrate
```

#### Create Superuser (Optional):
```bash
python manage.py createsuperuser
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

---

## Training Models

### 1. Prepare Dataset

Ensure `data/sample_sms_dataset.csv` exists with columns:
- `message` or `text`: SMS text content
- `category` or `label`: Classification label

### 2. Run Training Script

```bash
cd backend
python train_models.py
```

This will:
- Load and preprocess data
- Train multiple ML models (Naive Bayes, Logistic Regression, Random Forest, etc.)
- Perform cross-validation
- Evaluate performance
- Save the best model

### 3. Verify Training

Check `backend/ml_models/trained_models/` for:
- `best_model.pkl` - Trained pipeline
- `label_encoder.pkl` - Label encoder
- `model_metadata.json` - Model information
- `training_summary.csv` - Performance comparison

---

## Running the Application

### Development Mode

#### Terminal 1 - Backend:
```bash
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
python manage.py runserver
```

Backend will run on: `http://localhost:8000`

#### Terminal 2 - Frontend:
```bash
cd frontend
npm start
```

Frontend will run on: `http://localhost:3000`

### Access the Application

Open browser and navigate to: `http://localhost:3000`

---

## Production Deployment

### 1. Environment Configuration

Create `.env` file in backend directory:
```env
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com
DATABASE_URL=postgresql://user:password@localhost/dbname
REDIS_URL=redis://localhost:6379/0
ENABLE_CACHING=True
ENABLE_DEEP_LEARNING=True
```

### 2. Backend Production Setup

#### Install Production Server:
```bash
pip install gunicorn psycopg2-binary
```

#### Collect Static Files:
```bash
python manage.py collectstatic --noinput
```

#### Run with Gunicorn:
```bash
gunicorn sms_security.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --threads 2 \
    --timeout 60 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log
```

### 3. Frontend Production Build

```bash
cd frontend
npm run build
```

Serve the `build/` directory with Nginx or Apache.

### 4. Nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    # Frontend
    location / {
        root /path/to/frontend/build;
        try_files $uri /index.html;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files
    location /static/ {
        alias /path/to/backend/staticfiles/;
    }
}
```

### 5. Database Migration (PostgreSQL)

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb sms_security

# Update settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sms_security',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Run migrations
python manage.py migrate
```

### 6. Redis Setup (Caching)

```bash
# Install Redis
sudo apt-get install redis-server

# Start Redis
sudo systemctl start redis
sudo systemctl enable redis

# Update settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### 7. Systemd Service (Linux)

Create `/etc/systemd/system/sms-security.service`:
```ini
[Unit]
Description=SMS Security Assistant
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn sms_security.wsgi:application --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable sms-security
sudo systemctl start sms-security
```

---

## Monitoring & Maintenance

### 1. Health Checks

```bash
# API Health
curl http://localhost:8000/api/health/

# System Metrics
curl http://localhost:8000/api/metrics/

# Model Info
curl http://localhost:8000/api/model-info/
```

### 2. Log Monitoring

```bash
# View logs
tail -f backend/logs/sms_security.log

# Error logs
tail -f backend/logs/error.log
```

### 3. Performance Monitoring

Access metrics endpoint:
```
GET /api/metrics/
```

Returns:
- System resources (CPU, Memory, Disk)
- API usage statistics
- Model performance metrics
- Response time percentiles

### 4. Database Backup

```bash
# SQLite
cp backend/db.sqlite3 backup/db_$(date +%Y%m%d).sqlite3

# PostgreSQL
pg_dump sms_security > backup/db_$(date +%Y%m%d).sql
```

### 5. Model Retraining

```bash
# Retrain with new data
python train_models.py

# Restart application to load new model
sudo systemctl restart sms-security
```

---

## Troubleshooting

### Common Issues:

#### 1. Model Not Found Error
```
Solution: Run python train_models.py to train models
```

#### 2. Port Already in Use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/macOS
lsof -ti:8000 | xargs kill -9
```

#### 3. CORS Errors
```
Solution: Check CORS_ALLOWED_ORIGINS in settings.py
Ensure frontend URL is included
```

#### 4. Slow Predictions
```
Solution: 
- Enable caching (ENABLE_CACHING=True)
- Increase cache timeout
- Check system resources
- Consider using Redis
```

#### 5. Database Migration Errors
```bash
# Reset migrations (development only)
python manage.py migrate --fake api zero
python manage.py migrate
```

---

## Performance Tuning

### Backend Optimization:
1. Enable caching (Redis recommended)
2. Use connection pooling
3. Optimize database queries
4. Increase Gunicorn workers
5. Use CDN for static files

### Frontend Optimization:
1. Enable production build
2. Use code splitting
3. Implement lazy loading
4. Optimize images
5. Enable gzip compression

---

## Security Checklist

- [ ] Change SECRET_KEY in production
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Enable HTTPS
- [ ] Set up CSRF protection
- [ ] Configure rate limiting
- [ ] Regular security updates
- [ ] Database backups
- [ ] Log monitoring
- [ ] Access control

---

## Support & Documentation

### API Documentation:
- Swagger/OpenAPI: `/api/docs/`
- Postman Collection: `docs/postman_collection.json`

### Additional Resources:
- Architecture: `PROJECT_ARCHITECTURE.md`
- API Reference: `docs/API_REFERENCE.md`
- Model Documentation: `docs/MODEL_DOCUMENTATION.md`

---

## Contact & Contribution

For issues, questions, or contributions:
- GitHub Issues: <repository-url>/issues
- Email: <your-email>
- Documentation: <docs-url>

---

**Last Updated**: April 2026
**Version**: 2.0.0
**Status**: Production Ready
