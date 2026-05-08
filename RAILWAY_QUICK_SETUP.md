# 🚂 Railway Quick Setup Guide

## The Problem You Had

Railway tried to deploy your entire project as a single Node.js app, but you have:
- **Backend**: Django (Python)
- **Frontend**: React (Node.js)

They need to be deployed **separately**.

## Quick Fix: Deploy in 2 Steps

### Step 1: Deploy Backend (5 minutes)

1. **Create New Project** on Railway
2. **Connect GitHub** repo
3. **Configure Service**:
   - Root Directory: `backend`
   - Start Command: `python manage.py migrate && gunicorn sms_security.wsgi:application --bind 0.0.0.0:$PORT`

4. **Add Environment Variables**:
   ```
   SECRET_KEY=<generate-random-key>
   DEBUG=False
   ALLOWED_HOSTS=*.railway.app
   ```

5. **Generate SECRET_KEY**:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(64))"
   ```

6. **Deploy** and copy the URL (e.g., `https://backend-xxx.railway.app`)

### Step 2: Deploy Frontend (5 minutes)

1. **Add New Service** to same project
2. **Connect same GitHub** repo
3. **Configure Service**:
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Start Command: `npx serve -s build -l $PORT`

4. **Add Environment Variable**:
   ```
   REACT_APP_API_URL=https://backend-xxx.railway.app
   ```
   (Use the backend URL from Step 1)

5. **Deploy** and copy the URL (e.g., `https://frontend-xxx.railway.app`)

### Step 3: Update Backend CORS (1 minute)

Go back to backend service and add:
```
CORS_ALLOWED_ORIGINS=https://frontend-xxx.railway.app
```
(Use the frontend URL from Step 2)

## Done! 🎉

Your app is now live:
- Backend API: `https://backend-xxx.railway.app`
- Frontend UI: `https://frontend-xxx.railway.app`

## Test It

1. Open frontend URL
2. Try analyzing a message
3. Check Dashboard

## Common Issues

### "No start command detected"
**Fix**: Set start command manually in Railway settings (see above)

### "CORS error"
**Fix**: Make sure `CORS_ALLOWED_ORIGINS` in backend includes your frontend URL

### "node_modules warning"
**Fix**: Add to `.gitignore`:
```
node_modules/
frontend/node_modules/
backend/venv/
```

Then remove from git:
```bash
git rm -r --cached node_modules frontend/node_modules
git commit -m "Remove node_modules"
git push
```

## Files Created for You

✅ `backend/railway.toml` - Backend configuration
✅ `backend/nixpacks.toml` - Build configuration
✅ `backend/Procfile` - Start command
✅ `backend/runtime.txt` - Python version
✅ `frontend/nixpacks.toml` - Frontend configuration
✅ `frontend/package.json` - Added `serve` dependency

## Need Help?

Read the full guide: `RAILWAY_DEPLOYMENT_GUIDE.txt`

## Cost

- Free tier: $5 credit/month (enough for testing)
- Production: ~$10/month for both services

## Next Steps

1. Add PostgreSQL database (recommended)
2. Set up custom domain
3. Enable monitoring
4. Configure auto-scaling

---

**Status**: Ready to deploy! Follow the 3 steps above. ⬆️
