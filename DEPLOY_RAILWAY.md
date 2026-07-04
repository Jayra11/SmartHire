# 🚂 Deploying to Railway (FREE Tier - $5/month credits)

Railway offers a simple, modern deployment platform with $5/month free credits perfect for Jetski SmartHire.

## Getting Started

### 1. Install Railway CLI

```bash
# Using npm
npm install -g @railway/cli

# Or using brew (macOS)
brew install railway
```

### 2. Login to Railway

```bash
railway login
# Opens browser to authorize your account
```

### 3. Create New Project

```bash
cd jetski-smarthire
railway init
# Follow prompts to create new project
```

## Deploy Backend

### 1. Setup Backend Environment

```bash
# Set Python version
railway variables set PYTHON_VERSION 3.11

# Add Google Gemini API key
railway variables set GOOGLE_API_KEY AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Set production environment
railway variables set ENVIRONMENT production
```

### 2. Deploy Backend Service

```bash
cd backend

# Create Procfile
cat > Procfile << EOF
web: uvicorn main:app --host 0.0.0.0 --port \$PORT
EOF

# Add to git
git add .

# Deploy with Railway
railway up
```

**Railway will:**
- Detect Python environment
- Install dependencies from requirements.txt
- Run the start command
- Assign a public URL

Note the backend URL (e.g., `https://jetski-backend-prod.up.railway.app`)

## Deploy Frontend

### 1. Setup Frontend Service

```bash
cd frontend

# Create Procfile
cat > Procfile << EOF
web: npm run build && npm start
EOF

# Set environment variable
railway variables set REACT_APP_API_URL https://jetski-backend-prod.up.railway.app
```

### 2. Deploy Frontend

```bash
railway up
```

## Access Your Application

- **Frontend**: `https://jetski-frontend-prod.up.railway.app`
- **Backend API**: `https://jetski-backend-prod.up.railway.app`
- **API Docs**: `https://jetski-backend-prod.up.railway.app/docs`

## Manage Deployments

```bash
# View logs
railway logs

# List deployments
railway deployments

# View variables
railway variables

# View status
railway status

# Open dashboard
railway open
```

## Cost Tracking

Railway gives $5/month free credit. Monitor usage:

```bash
# In dashboard, navigate to Account → Billing
# Set budget alerts to avoid overage charges
```

## Automatic Deployments from GitHub

1. Go to Railway Dashboard
2. Select your project
3. Click **Project Settings**
4. Scroll to **GitHub Integration**
5. Enable automatic deploys from your repository

## Custom Domain (Optional)

1. In Railway Dashboard, go to your project
2. Click service (frontend or backend)
3. Go to **Settings** tab
4. Add custom domain under **Domain**
5. Update DNS records with provided values

## Environment Variables

Update via CLI:
```bash
railway variables set VAR_NAME value
```

Or in Dashboard:
1. Select service
2. Click **Variables** tab
3. Add/edit variables

## Database (Optional - PostgreSQL)

Add PostgreSQL database:

```bash
# In Railway Dashboard
# Click "Add Service" → PostgreSQL
# Get connection string from variables
# Use in your application
```

## Monitoring & Logs

```bash
# Stream real-time logs
railway logs -f

# View specific deployment logs
railway logs --deployment <id>

# Tail last N logs
railway logs --lines 50
```

## Troubleshooting

### "Port already in use"
```bash
# Railway assigns PORT via environment variable
# Ensure app uses: port = int(os.getenv('PORT', 8000))
```

### "Deployment failed"
```bash
# Check logs
railway logs

# Verify Procfile is correct
# Ensure requirements.txt has all dependencies
```

### Environment variables not loading
```bash
# Redeploy after adding variables
railway up

# Verify with:
railway variables
```

### Frontend can't reach backend
```bash
# Verify REACT_APP_API_URL is set correctly
# Check it matches backend URL
railway variables
```

## Performance Tips

1. **Enable caching**:
   ```bash
   railway variables set NODE_ENV production
   ```

2. **Optimize builds**:
   - Remove unused dependencies
   - Use npm ci instead of npm install

3. **Monitor resource usage**:
   - View in Railway Dashboard → Metrics
   - Scale up if needed

## Rollback to Previous Deployment

```bash
# List deployments
railway deployments

# View specific deployment
railway deployment <id>

# Railway Dashboard: Click deployment → Redeploy
```

## Update Application

```bash
# Make code changes locally
git add .
git commit -m "Update feature"
git push origin main

# Redeploy
railway up
```

## Comparison: Railway vs Alternatives

| Feature | Railway | Render | Heroku |
|---------|---------|--------|--------|
| Free Tier | $5/mo | Yes | No |
| Ease | Very Easy | Easy | Medium |
| Speed | Fast | Medium | Slow |
| Support | Good | Excellent | Limited |
| Database | Yes | Yes | Yes |

## Next Steps

1. ✅ Deploy backend and frontend
2. ✅ Test end-to-end functionality
3. ✅ Configure auto-deployments
4. ✅ Set up monitoring
5. ✅ Add custom domain

---

**Railway Dashboard**: https://railway.app
**Docs**: https://docs.railway.app
