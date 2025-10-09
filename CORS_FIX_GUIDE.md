# CORS Fix Guide for Railway Deployment

## Problem
Your frontend running on `http://localhost:3000` cannot make API requests to your production backend at `https://price-regulator-frontend-backend-production.up.railway.app` due to CORS (Cross-Origin Resource Sharing) restrictions.

## Solution
You need to update your Railway deployment to allow requests from `localhost:3000`.

## Option 1: Update Railway Environment Variables (Recommended)

1. **Go to your Railway dashboard**: https://railway.app/dashboard
2. **Select your backend project**: `price-regulator-frontend-backend-production`
3. **Go to Variables tab**
4. **Add/Update these environment variables**:

```bash
# Add this environment variable
ADDITIONAL_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

5. **Redeploy your backend** (Railway should auto-deploy when you add environment variables)

## Option 2: Update CORS_ALLOWED_ORIGINS

Alternatively, you can update the existing `CORS_ALLOWED_ORIGINS` environment variable:

```bash
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com,http://localhost:3000,http://127.0.0.1:3000
```

## Option 3: Temporary Development Override

For immediate testing, you can temporarily enable all origins (NOT recommended for production):

```bash
DEBUG=True
```

This will enable `CORS_ALLOW_ALL_ORIGINS = True` in the production settings.

## Verification

After updating the environment variables and redeploying:

1. **Check the deployment logs** in Railway to ensure the backend restarted
2. **Test the API** by making a request from your frontend
3. **Check browser console** - the CORS error should be gone

## Expected Result

After the fix, you should see:
- ✅ No CORS errors in browser console
- ✅ Successful API requests to `https://price-regulator-frontend-backend-production.up.railway.app/api/auth/login/`
- ✅ Login functionality working from `http://localhost:3000`

## Security Note

Allowing `localhost:3000` in production CORS settings is generally safe for development purposes, but you should:
- Remove localhost origins when deploying your frontend to production
- Use specific domains instead of wildcards in production
- Regularly review and update your CORS settings

## Quick Test

After making the changes, test with this curl command:

```bash
curl -X POST https://price-regulator-frontend-backend-production.up.railway.app/api/auth/login/ \
  -H "Content-Type: application/json" \
  -H "Origin: http://localhost:3000" \
  -d '{"email":"admin@example.com","password":"admin123","device_id":"test"}'
```

You should get a response instead of a CORS error.
