# 🚀 Deploying to Render (FREE)

Render is the easiest way to deploy Jetski SmartHire with a generous free tier.

## What's Included in Free Tier

✅ Backend Web Service: $7/month (Free for first 3 months)
✅ Frontend Static Site: FREE forever
✅ Automatic deployments from GitHub
✅ SSL/HTTPS by default
✅ Environment variables support

## Step-by-Step Deployment

### 1. Prepare Your Repository

```bash
# Ensure everything is committed
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### 2. Backend Deployment

#### Create Backend Service

1. Go to https://dashboard.render.com
2. Click **New +** → **Web Service**
3. Select **Build and deploy from a Git repository**
4. Click **Connect GitHub** and authorize
5. Find and select `jetski-smarthire` repository

#### Configure Backend

| Setting | Value |
|---------|-------|
| Name | `jetski-backend` |
| Environment | `Python 3` |
| Build Command | `pip install -r backend/requirements.txt` |
| Start Command | `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Plan | Free (or Starter if you need reliability) |

#### Add Environment Variables

Click **Environment** tab:

```
GOOGLE_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxx
ENVIRONMENT=production
```

Click **Create Web Service**

**Wait for deployment to complete (~5 minutes)**

Copy the backend URL (e.g., `https://jetski-backend.onrender.com`)

### 3. Frontend Deployment

#### Method A: Static Site (Recommended)

1. In Render dashboard, click **New +** → **Static Site**
2. Connect your GitHub repository
3. Configure:

| Setting | Value |
|---------|-------|
| Name | `jetski-frontend` |
| Build Command | `cd frontend && npm install && npm run build` |
| Publish Directory | `frontend/build` |
| Environment Variables | See below |

#### Add Frontend Environment Variable

Click **Environment**:

```
REACT_APP_API_URL=https://jetski-backend.onrender.com
```

Click **Create Static Site**

#### Method B: Web Service (if Static Site doesn't work)

1. Click **New +** → **Web Service**
2. Select repository and configure:

| Setting | Value |
|---------|-------|
| Name | `jetski-frontend` |
| Environment | `Node` |
| Build Command | `cd frontend && npm install && npm run build` |
| Start Command | `cd frontend && npm start` |
| Plan | Free |

Add environment variable:
```
REACT_APP_API_URL=https://jetski-backend.onrender.com
```

### 4. Enable Auto-Deployments

1. Go to **Settings** tab in Render dashboard
2. Enable **Auto-Deploy**
3. Select **Deploy new commits to production**

### 5. Test Your Deployment

1. Open frontend URL (e.g., `https://jetski-frontend.onrender.com`)
2. Upload a test resume
3. Verify it processes correctly

## URLs After Deployment

- **Frontend**: `https://jetski-frontend.onrender.com`
- **Backend API**: `https://jetski-backend.onrender.com`
- **API Docs**: `https://jetski-backend.onrender.com/docs`

## Troubleshooting

### Backend shows "504 Gateway Timeout"
```
→ Render needs ~2 minutes to start Python services
→ Wait a bit longer and refresh
→ Check logs in Render dashboard: Settings → Logs
```

### Frontend shows API errors
```
→ Verify REACT_APP_API_URL is correct
→ Check backend is deployed and running
→ Clear browser cache
```

### "Build failed" error
```
→ Check build logs in Render dashboard
→ Ensure all dependencies in requirements.txt
→ Verify Python version is 3.11+
```

### CORS errors
```
→ Backend CORS is configured for all origins
→ If still issues, check browser console for exact error
```

## Cost Estimation

**Monthly cost (after free period):**
- Backend Web Service: $7/month
- Frontend Static Site: FREE
- **Total: $7/month (or less with discounts)**

## Scaling

As your app grows:

1. **Upgrade Backend Plan**: Settings → Plan → Choose Starter or Pro
2. **Add Caching**: Render's Redis add-on
3. **Add Database**: PostgreSQL add-on for persistent storage

## Custom Domain

1. In Render dashboard, go to **Settings**
2. Scroll to **Custom Domain**
3. Add your domain (e.g., `hire.yourcompany.com`)
4. Update DNS records as instructed

## GitHub Secrets (Optional)

For automatic deployments, add to GitHub:

```
Settings → Secrets and Variables → Actions

RENDER_DEPLOY_HOOK=https://api.render.com/deploy/...
GOOGLE_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Monitoring

View in Render Dashboard:
- **Metrics**: CPU, Memory, Bandwidth usage
- **Logs**: Real-time application logs
- **Deploys**: Deployment history and status

## Next Steps

1. ✅ Verify both services are running
2. ✅ Test end-to-end functionality
3. ✅ Monitor logs for errors
4. ✅ Share deployment URL
5. ✅ Set up custom domain (optional)

---

Need help? Check Render's [documentation](https://render.com/docs)
