# 🛡️ SMS Security Assistant

An AI-powered SMS classification and security analysis system that detects spam, phishing, and categorizes messages using machine learning.

## 🌟 Features

- **Real-time SMS Analysis** - Instant classification of messages
- **Multi-Model ML** - 5 different ML models with 86.67% accuracy
- **Phishing Detection** - Advanced phishing attempt identification
- **Risk Assessment** - Comprehensive risk level analysis
- **Sentiment Analysis** - Emotional tone detection
- **Multi-language Support** - English, Hindi, and Marathi
- **Professional Dashboard** - Analytics and message history
- **Mobile Responsive** - Works on all devices

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### Installation

**1. Clone the repository**
```bash
git clone <your-repo-url>
cd <project-folder>
```

**2. Setup Backend**
```bash
cd backend
python -m venv venv
venv\Scripts\activate              # Windows
# OR
source venv/bin/activate           # Mac/Linux

pip install -r requirements.txt
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"
python manage.py migrate
python manage.py runserver
```

**3. Setup Frontend** (New Terminal)
```bash
cd frontend
npm install
npm start
```

**4. Open Browser**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## 📁 Project Structure

```
project/
├── backend/              # Django REST API
│   ├── api/             # API endpoints
│   ├── ml_models/       # ML models & training
│   └── manage.py        # Django management
│
├── frontend/            # React UI
│   ├── src/            # Source code
│   └── public/         # Static files
│
├── android/            # Android app (optional)
├── data/              # Training datasets
└── docs/              # Documentation
```

## 🎯 Usage

### Analyze a Message
1. Go to Home page
2. Enter SMS message
3. Select language
4. Click "Analyze Message"
5. View detailed results

### View Dashboard
- Statistics and analytics
- Message history
- Filter by category/risk
- View/delete messages

## 🧠 ML Models

The system uses 5 machine learning models:
- Naive Bayes + TF-IDF (Best: 86.67%)
- Logistic Regression
- Random Forest
- Gradient Boosting
- SVM

## 🔧 Configuration

### Backend (.env)
```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:8000
```

## 📊 API Endpoints

- `POST /api/predict/` - Analyze SMS message
- `GET /api/stats/` - Get statistics
- `GET /api/recent-messages/` - Get message history
- `GET /api/model-info/` - Get model information
- `POST /api/reset/` - Reset all data

## 🚢 Deployment

### Railway (Recommended)
See [RAILWAY_QUICK_SETUP.md](RAILWAY_QUICK_SETUP.md) for deployment guide.

### Manual Deployment
1. Deploy backend and frontend separately
2. Set environment variables
3. Configure CORS
4. Use PostgreSQL for production

## 🧪 Testing

### Test Model Accuracy
```bash
cd backend
python test_accuracy.py
```

### Train New Models
```bash
cd backend
python train_models.py
```

## 📱 Mobile Access

### Android App
See `android/` folder for native Android app.

### Web on Mobile
1. Find your IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
2. Start backend: `python manage.py runserver 0.0.0.0:8000`
3. Update frontend `.env`: `REACT_APP_API_URL=http://YOUR_IP:8000`
4. Access from phone: `http://YOUR_IP:3000`

## 🛠️ Development

### Backend Commands
```bash
python manage.py runserver         # Start server
python manage.py migrate           # Run migrations
python manage.py createsuperuser   # Create admin
python test_accuracy.py            # Test models
```

### Frontend Commands
```bash
npm start                          # Development server
npm run build                      # Production build
npm test                           # Run tests
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9
```

### Module Not Found
```bash
# Backend
pip install -r requirements.txt

# Frontend
npm install
```

### CORS Errors
- Verify backend CORS_ALLOWED_ORIGINS includes frontend URL
- Check browser console for specific errors

## 📚 Documentation

- [Quick Start Guide](QUICK_START.txt)
- [Detailed Setup](HOW_TO_RUN_PROJECT.md)
- [Railway Deployment](RAILWAY_QUICK_SETUP.md)
- [Accuracy Report](PROJECT_ACCURACY_REPORT.md)

## 🔐 Security Features

- Rate limiting
- API key authentication
- CSRF protection
- XSS prevention
- SQL injection protection
- Secure headers
- HTTPS enforcement (production)

## 🎨 Tech Stack

### Backend
- Django 4.2
- Django REST Framework
- scikit-learn
- NLTK
- pandas, numpy

### Frontend
- React 18
- React Router
- Axios
- Bootstrap 5
- Chart.js

### ML/AI
- Naive Bayes
- TF-IDF Vectorization
- Sentiment Analysis
- Pattern Recognition
- Ensemble Learning

## 📈 Performance

- **Accuracy**: 86.67%
- **Precision**: 87.01%
- **Recall**: 86.55%
- **F1-Score**: 86.60%
- **Response Time**: <100ms

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open pull request

## 📄 License

This project is licensed under the MIT License.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- SMS dataset providers
- Open source ML libraries
- Django and React communities

## 📞 Support

For issues and questions:
- Check [HOW_TO_RUN_PROJECT.md](HOW_TO_RUN_PROJECT.md)
- Open an issue on GitHub
- Check browser console (F12)

## 🗺️ Roadmap

- [ ] Real-time SMS monitoring
- [ ] Email integration
- [ ] Advanced threat intelligence
- [ ] Multi-user support
- [ ] API rate limiting dashboard
- [ ] Automated model retraining

---

**Status**: Production Ready ✅

**Version**: 2.0.0

**Last Updated**: May 2026
