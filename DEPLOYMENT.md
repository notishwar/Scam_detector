# 🚀 Deployment Guide

This guide covers deploying your Agentic Honey-Pot to production using **free hosting services**.

---

## 🎯 Quick Deploy Options

### Option 1: Railway (Recommended - Easiest)
**All-in-one deployment for both backend and frontend**

#### Step 1: Prepare for Railway
1. Create `railway.json` (already created)
2. Push code to GitHub

#### Step 2: Deploy
1. Go to [Railway.app](https://railway.app)
2. Sign up with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select your `honeypot-scam-ai` repository
5. Railway will auto-detect FastAPI and deploy!

#### Step 3: Configure
1. In Railway dashboard, go to **Variables**
2. Add: `PORT=8000`
3. Get your backend URL: `https://your-app.railway.app`

#### Step 4: Update Frontend
Edit `frontend/app.js` line 7:
```javascript
backendUrl: 'https://your-app.railway.app',
```

#### Step 5: Deploy Frontend
1. Create new Railway service
2. Deploy the `frontend` folder
3. You're live! 🎉

**Cost:** FREE $5/month credit (enough for this project)

---

### Option 2: Render (Backend) + Vercel (Frontend)

#### Backend on Render

##### Step 1: Create `render.yaml`
Already created in your project root.

##### Step 2: Deploy to Render
1. Go to [Render.com](https://render.com)
2. Sign up with GitHub
3. Click **"New+"** → **"Web Service"**
4. Connect your GitHub repo
5. Configure:
   - **Name:** `honeypot-backend`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Click **"Create Web Service"**

##### Step 3: Get Backend URL
Copy your Render URL: `https://honeypot-backend.onrender.com`

#### Frontend on Vercel

##### Step 1: Update Backend URL
Edit `frontend/app.js` line 7:
```javascript
backendUrl: 'https://honeypot-backend.onrender.com',
```

##### Step 2: Deploy to Vercel
1. Go to [Vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Click **"Add New"** → **"Project"**
4. Select your GitHub repo
5. Configure:
   - **Framework Preset:** Other
   - **Root Directory:** `frontend`
   - **Build Command:** (leave empty)
   - **Output Directory:** `.`
6. Click **"Deploy"**

You're live at: `https://your-app.vercel.app` 🎉

**Cost:** FREE forever

---

### Option 3: Netlify (Frontend Only - API Proxy)

If you want frontend on Netlify with serverless functions:

##### Step 1: Create Netlify Function
Create `frontend/netlify/functions/api.js`:
```javascript
exports.handler = async (event, context) => {
  // Proxy to your backend or use serverless LLM calls
  return {
    statusCode: 200,
    body: JSON.stringify({ message: "API endpoint" })
  };
};
```

##### Step 2: Deploy
1. Go to [Netlify.com](https://netlify.com)
2. Drag & drop `frontend` folder
3. Configure in `netlify.toml` (already created)

**Cost:** FREE forever

---

## 🔧 Environment Variables

For production, you'll need to set:

### Backend (Render/Railway)
```
PORT=8000
ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

### Frontend (Update in code before deploy)
Update `frontend/app.js`:
```javascript
backendUrl: 'https://your-backend.onrender.com',
```

---

## 📝 Pre-Deployment Checklist

- [ ] Push code to GitHub
- [ ] Update CORS origins in `backend/app/main.py`
- [ ] Update frontend backend URL
- [ ] Test locally one last time
- [ ] Deploy backend first
- [ ] Then deploy frontend with correct backend URL

---

## 🌐 Custom Domain (Optional)

### Railway
1. Go to Settings → Domains
2. Add your custom domain
3. Update DNS records

### Vercel/Netlify
1. Go to Settings → Domains
2. Add custom domain
3. Follow DNS setup instructions

---

## 🐛 Troubleshooting

### Backend won't start
- Check `requirements.txt` is in `backend/` folder
- Verify start command includes `cd backend`
- Check logs in hosting dashboard

### Frontend can't connect
- Verify backend URL in `frontend/app.js`
- Check CORS settings in `backend/app/main.py`
- Ensure backend is running (visit the URL)

### CORS Error
Update `backend/app/main.py` line 16:
```python
allow_origins=["https://your-frontend.vercel.app"],
```

---

## 💡 Recommended: Railway (Fastest)

**Why Railway?**
- ✅ Auto-detects FastAPI
- ✅ Free $5/month credit
- ✅ Easy setup (5 minutes)
- ✅ Custom domain support
- ✅ Auto-deploy on git push

**Follow Option 1 above for quickest deployment!**
