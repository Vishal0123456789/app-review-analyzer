# Deployment Guide: Railway + Vercel

This guide walks you through deploying the App Review Insights Analyzer to Railway (backend) and Vercel (frontend).

## Prerequisites

1. **GitHub Account** - https://github.com
2. **Railway Account** - https://railway.app
3. **Vercel Account** - https://vercel.com
4. **Git installed** - https://git-scm.com

## Step 1: Prepare Your Code for GitHub

### 1.1 Initialize Git (if not already done)

```powershell
cd "c:\Users\satis\Milestone 2"
git init
git add .
git commit -m "Initial commit for deployment"
```

### 1.2 Create GitHub Repository

1. Go to https://github.com/new
2. Create new repository: `app-review-analyzer`
3. **Do NOT** initialize with README, .gitignore, or license
4. Click "Create repository"

### 1.3 Push Code to GitHub

```powershell
# Add remote
git remote add origin https://github.com/YOUR_USERNAME/app-review-analyzer.git
git branch -M main
git push -u origin main
```

**Replace `YOUR_USERNAME` with your GitHub username**

---

## Step 2: Deploy Backend on Railway

### 2.1 Create Railway Account & Project

1. Go to https://railway.app
2. Sign up with GitHub (recommended)
3. Click "New Project"
4. Select "GitHub Repo"

### 2.2 Connect GitHub Repository

1. Authorize Railway to access GitHub
2. Select your `app-review-analyzer` repository
3. Railway auto-detects the Dockerfile
4. Click "Deploy"

**Wait for deployment to complete (~5 minutes)**

### 2.3 Get Your Railway URL

1. Once deployed, go to "Deployments" tab
2. Copy the URL (e.g., `https://app-review-analyzer-prod.railway.app`)
3. Save this for later

### 2.4 Set Environment Variables on Railway

1. In Railway Dashboard, go to "Variables"
2. Add the following variables:

```
GEMINI_API_KEY = your-gemini-api-key-here
DEFAULT_EMAIL = agraharivishal19981@gmail.com
TO_EMAILS = recipient@example.com
SMTP_USERNAME = your-gmail@gmail.com
SMTP_PASSWORD = your-gmail-app-password
SMTP_HOST = smtp.gmail.com
SMTP_PORT = 587
```

3. Click "Save" to redeploy with environment variables

**Get these values:**
- **GEMINI_API_KEY**: https://aistudio.google.com/app/apikeys
- **SMTP_PASSWORD**: Google App Password (https://myaccount.google.com/apppasswords)

---

## Step 3: Deploy Frontend on Vercel

### 3.1 Import Project to Vercel

1. Go to https://vercel.com
2. Click "New Project"
3. Select "Import Git Repository"
4. Find and select `app-review-analyzer`
5. Click "Import"

### 3.2 Configure Build Settings

In the import dialog, set:

**Framework Preset:** Vite
**Root Directory:** `frontend`
**Build Command:** `npm run build`
**Output Directory:** `dist`

### 3.3 Add Environment Variables

Before deploying, click "Environment Variables" and add:

```
VITE_API_URL = https://your-railway-url.railway.app
```

**Replace with your actual Railway URL from Step 2.3**

### 3.4 Deploy

Click "Deploy" and wait for completion (~3 minutes)

Once complete, you'll get a Vercel URL (e.g., `https://app-review-analyzer.vercel.app`)

---

## Step 4: Verify Deployment

### 4.1 Test Backend (Railway)

```powershell
# Test orchestrator endpoint
curl https://your-railway-url.railway.app/api/analyze -X POST `
  -H "Content-Type: application/json" `
  -d '{"window_days": 7, "email": ""}'
```

### 4.2 Test Frontend (Vercel)

1. Open https://your-vercel-url.vercel.app
2. You should see the App Review Insights interface
3. Try submitting an analysis
4. Verify results appear

---

## Step 5: Gmail Setup (Important!)

To enable email sending, you need to:

### 5.1 Enable 2-Factor Authentication

1. Go to https://myaccount.google.com/security
2. Turn on "2-Step Verification"

### 5.2 Create App Password

1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer"
3. Copy the 16-character password
4. Use this as `SMTP_PASSWORD` in Railway

---

## Step 6: Monitor Your Deployment

### 6.1 View Railway Logs

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# View logs
railway logs -f
```

### 6.2 Check Vercel Analytics

Visit Vercel Dashboard → Your Project → Analytics

---

## Troubleshooting

### Backend Won't Deploy

1. Check Railway logs: `railway logs -f`
2. Verify environment variables are set
3. Ensure SMTP credentials are correct

### Frontend Shows Blank

1. Check browser console for errors (F12)
2. Verify `VITE_API_URL` matches Railway URL
3. Make sure Railway backend is running

### Emails Not Sending

1. Verify Gmail app password in SMTP_PASSWORD
2. Check Railway logs for SMTP errors
3. Confirm sender email matches SMTP_USERNAME

### Can't Connect Frontend to Backend

1. Check Railway URL in `VITE_API_URL`
2. Ensure Railway backend is healthy
3. Check CORS settings in `app.py`

---

## Next Steps

1. **Monitor:** Check logs regularly
2. **Update:** Deploy changes via `git push`
3. **Scale:** Add Railway volumes if needed
4. **Analyze:** Use the web interface for weekly reports

---

## Quick Command Reference

```bash
# Local testing
cd frontend && npm run dev          # Start frontend dev server
python -m uvicorn app:app --reload # Start backend locally

# GitHub updates
git add .
git commit -m "Your message"
git push origin main

# Railway
railway login
railway logs -f

# Vercel redeploy
# Automatic on git push, or redeploy from dashboard
```

---

## Support

- Railway Docs: https://docs.railway.app
- Vercel Docs: https://vercel.com/docs
- FastAPI Docs: https://fastapi.tiangolo.com
- React Docs: https://react.dev
