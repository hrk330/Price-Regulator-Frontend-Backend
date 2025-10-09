# Environment Configuration Guide

This frontend application now includes automatic environment detection for API URLs. The system will automatically determine whether to use the local development API or the production API based on the current environment.

## How It Works

### Automatic Detection Logic

The system automatically detects the environment using the following logic:

1. **User Preferences (Highest Priority):**
   - If you've set a preference in localStorage, it will use that
   - You can force production API even on localhost
   - You can force local API even on production domains

2. **Local Development Detection:**
   - If running on `localhost`, `127.0.0.1`, or local network IPs (192.168.x.x, 10.x.x.x)
   - Uses: `http://localhost:8000/api` (unless overridden)

3. **Production Detection:**
   - If running on Railway, Vercel, Netlify, or other production domains
   - Uses: `https://price-regulator-frontend-backend-production.up.railway.app/api`

4. **Custom Override:**
   - If `NEXT_PUBLIC_API_URL` environment variable is set, it will use that instead

### Environment Files

#### For Local Development
Create a `.env.local` file in the frontend directory:
```bash
# Optional - system will auto-detect localhost
# NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

#### For Production
Set the environment variable in your deployment platform:
```bash
# Optional - system will auto-detect production domains
# NEXT_PUBLIC_API_URL=https://price-regulator-frontend-backend-production.up.railway.app/api
```

## Usage

### In Your Components
The API configuration is automatically handled. You don't need to change anything in your existing code:

```typescript
import { api, authApi, productsApi } from '@/lib/api'

// These will automatically use the correct API URL
const products = await productsApi.list()
const user = await authApi.me()
```

### Debugging Environment Info
You can add the debug component to see which API URL is being used and control it:

```tsx
import EnvironmentInfo from '@/components/debug/EnvironmentInfo'

export default function MyPage() {
  return (
    <div>
      {/* Your page content */}
      
      {/* Debug info (only shows in development) */}
      <EnvironmentInfo />
    </div>
  )
}
```

The debug component includes:
- **Show/Hide Environment Info**: Toggle button in bottom-right corner
- **Current API URL**: Shows which API is currently being used
- **Environment Details**: Hostname, Node environment, etc.
- **API Controls**: Buttons to switch between APIs:
  - **Use Production API**: Forces production API even on localhost
  - **Use Local API**: Forces local API even on production
  - **Auto Detect**: Resets to automatic detection

### Manual Environment Check
You can also check and control the environment programmatically:

```typescript
import { 
  getApiUrl, 
  isDevelopment, 
  isProduction, 
  getEnvironmentInfo,
  forceProductionApi,
  forceLocalApi,
  resetApiUrl
} from '@/lib/config'

// Get the current API URL
const apiUrl = getApiUrl()

// Check environment
const isDev = isDevelopment()
const isProd = isProduction()

// Get full environment info
const envInfo = getEnvironmentInfo()
console.log(envInfo)

// Control API URL
forceProductionApi()  // Force production API even on localhost
forceLocalApi()       // Force local API even on production
resetApiUrl()         // Reset to automatic detection
```

## Deployment

### Railway Deployment
When deploying to Railway, the system will automatically detect the production environment and use the production API URL.

### Local Development
When running locally with `npm run dev`, the system will automatically detect localhost and use the local API URL.

### Custom Domains
If you deploy to a custom domain, you can either:
1. Set the `NEXT_PUBLIC_API_URL` environment variable
2. Modify the detection logic in `lib/config.ts` to include your domain

## Troubleshooting

### Check Current Configuration
1. Open browser developer tools
2. Look for the "🔧 API Configuration" log message
3. Or use the EnvironmentInfo debug component

### Force Specific API URL
If you need to override the automatic detection, set the environment variable:
```bash
NEXT_PUBLIC_API_URL=your-custom-api-url-here
```

### Common Issues
- **CORS errors**: Make sure your backend allows requests from your frontend domain
- **API not found**: Verify the API URL is correct and the backend is running
- **Environment not detected**: Check the hostname detection logic in `lib/config.ts`
