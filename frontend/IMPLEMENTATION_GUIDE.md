# 🚀 SmartCitySense Frontend - Complete Implementation Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Environment Configuration](#environment-configuration)
4. [Component Generation](#component-generation)
5. [Testing](#testing)
6. [Deployment](#deployment)
7. [Integration with Backend](#integration-with-backend)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- ✅ Node.js 18+ ([Download](https://nodejs.org/))
- ✅ npm or yarn
- ✅ Git
- ✅ Modern web browser (Chrome/Firefox/Safari)

### Required Accounts & API Keys
- ✅ [Mapbox Account](https://www.mapbox.com/) - For map visualization
- ✅ [Firebase Project](https://console.firebase.google.com/) - For auth, storage, FCM
- ✅ Backend API running on localhost:8000 (or deployed URL)

---

## Initial Setup

### Step 1: Navigate to Frontend Directory

```bash
cd /Users/kushagrakumar/Desktop/SmartCitySense/frontend
```

### Step 2: Make Scripts Executable

```bash
chmod +x setup.sh
chmod +x generate-components-part1.sh
chmod +x generate-components-part2.sh
chmod +x generate-components-final.sh
```

### Step 3: Run Setup Script

```bash
./setup.sh
```

This will:
- Install all npm dependencies
- Create necessary directory structure
- Setup Tailwind CSS with animations

**Expected Output:**
```
🚀 Setting up SmartCitySense Frontend...
📦 Installing dependencies...
...
✅ Basic setup complete!
```

---

## Environment Configuration

### Step 1: Create Environment File

```bash
cp .env.example .env.local
```

### Step 2: Get Mapbox Token

1. Go to https://account.mapbox.com/
2. Sign up or login
3. Navigate to "Access Tokens"
4. Create a new token or use default public token
5. Copy the token starting with `pk.`

### Step 3: Setup Firebase Project

#### 3.1 Create Firebase Project
1. Go to https://console.firebase.google.com/
2. Click "Add Project"
3. Enter project name (e.g., "smartcitysense")
4. Disable Google Analytics (optional)
5. Click "Create Project"

#### 3.2 Enable Authentication
1. In Firebase Console, go to "Authentication"
2. Click "Get Started"
3. Enable "Google" sign-in method
4. Enable "Email/Password" sign-in method

#### 3.3 Create Web App
1. Click Project Settings (gear icon)
2. Scroll to "Your apps"
3. Click Web icon (</>)
4. Register app with nickname "smartcitysense-frontend"
5. **Copy the configuration values**

#### 3.4 Enable Cloud Firestore
1. Go to "Firestore Database"
2. Click "Create database"
3. Start in "Test mode" (for development)
4. Choose location closest to your users

#### 3.5 Enable Storage
1. Go to "Storage"
2. Click "Get Started"
3. Start in "Test mode"

#### 3.6 Enable Cloud Messaging
1. Go to "Cloud Messaging"
2. Click "Get Started"
3. Generate VAPID key (for web push)
4. Copy the key pair

### Step 4: Fill .env.local File

```env
# Backend API (update if deployed)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Mapbox Token (from Step 2)
NEXT_PUBLIC_MAPBOX_TOKEN=pk.eyJ1IjoieW91cnVzZXJuYW1lIiwiYSI6InlvdXJ0b2tlbiJ9...

# Firebase Configuration (from Step 3.3)
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXX
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=smartcitysense.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=smartcitysense
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=smartcitysense.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789012
NEXT_PUBLIC_FIREBASE_APP_ID=1:123456789012:web:abc123def456
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=G-XXXXXXXXXX
NEXT_PUBLIC_FIREBASE_VAPID_KEY=BFb-XXX... (from Step 3.6)

# Default City Coordinates (Bengaluru - adjust if needed)
NEXT_PUBLIC_DEFAULT_LAT=12.9716
NEXT_PUBLIC_DEFAULT_LNG=77.5946
NEXT_PUBLIC_DEFAULT_ZOOM=11
```

---

## Component Generation

### Step 1: Generate Core Components

```bash
./generate-components-part1.sh
```

**Creates:**
- Header component with city stats
- Sidebar navigation
- Avatar component
- Dropdown menu component

### Step 2: Generate Map Components

```bash
./generate-components-part2.sh
```

**Creates:**
- MapView with Mapbox integration
- Event clustering with Supercluster
- Map filters panel
- Event detail drawer
- Dashboard main page
- Map page

### Step 3: Generate Remaining Components

```bash
./generate-components-final.sh
```

**Creates:**
- Reports page
- Alerts page
- Analytics page with charts
- Mood Map view
- Settings page
- Dialog component

---

## Testing

### Step 1: Start Backend Services

**Ensure these are running:**

```bash
# Terminal 1: Backend API
cd ../backend
python -m app.main

# Terminal 2: AI/ML Service (optional for full features)
cd ../ai-ml
python main.py

# Terminal 3: Data Ingestion (optional for live data)
cd ../data-ingestion
python main.py
```

### Step 2: Start Frontend Development Server

```bash
# In frontend directory
npm run dev
```

**Expected Output:**
```
▲ Next.js 14.2.3
- Local:        http://localhost:3000
- Ready in XXXms
```

### Step 3: Open Browser

Navigate to: **http://localhost:3000**

### Step 4: Test Authentication

1. You should be redirected to `/login`
2. Click "Sign in with Google" or use email/password
3. After successful login, you should see the dashboard

### Step 5: Test Core Features

#### Dashboard
- [ ] See stats cards (Events, Alerts, Sentiment, Resolved Issues)
- [ ] View recent events list
- [ ] See active alerts

#### Map View
- [ ] Navigate to "Map View" from sidebar
- [ ] See Mapbox map centered on your city
- [ ] Pan and zoom the map
- [ ] Toggle filters
- [ ] Click event markers
- [ ] See event details in bottom drawer

#### Reports
- [ ] Click "New Report" button
- [ ] Should open report form (if implemented)
- [ ] View existing reports

#### Alerts
- [ ] See list of active alerts
- [ ] Color-coded by severity
- [ ] See predictive alerts (if AI/ML service running)

#### Analytics
- [ ] View event volume chart
- [ ] See category distribution
- [ ] Check city health score

#### Mood Map
- [ ] View sentiment-colored zones
- [ ] Hover over markers for details

#### Settings
- [ ] See user profile
- [ ] View email and avatar

---

## Deployment

### Option 1: Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel

# Set environment variables in Vercel dashboard
```

### Option 2: Docker

```bash
# Build image
docker build -t smartcitysense-frontend .

# Run container
docker run -p 3000:3000 --env-file .env.local smartcitysense-frontend
```

### Option 3: Traditional Server

```bash
# Build for production
npm run build

# Start production server
npm start
```

---

## Integration with Backend

### API Endpoint Configuration

The frontend expects these backend endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/events` | List all events |
| GET | `/events/:id` | Get single event |
| POST | `/reports` | Create report |
| GET | `/reports` | List reports |
| GET | `/alerts` | List alerts |
| GET | `/sentiments` | Sentiment data |
| GET | `/stats` | City statistics |
| GET | `/analytics` | Analytics data |
| POST | `/subscriptions` | Create subscription |
| GET | `/subscriptions/:userId` | Get subscriptions |
| DELETE | `/subscriptions/:id` | Delete subscription |

### CORS Configuration

Ensure your backend allows requests from frontend origin:

**FastAPI Example (backend/app/main.py):**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Authentication Flow

1. User logs in via Firebase Auth
2. Frontend gets ID token: `user.getIdToken()`
3. Token sent to backend in `Authorization: Bearer <token>` header
4. Backend verifies token with Firebase Admin SDK

---

## Troubleshooting

### Issue: Map Not Loading

**Symptoms:** Blank screen where map should be

**Solutions:**
1. Check Mapbox token is correct in `.env.local`
2. Verify token starts with `pk.`
3. Check browser console for errors
4. Ensure `NEXT_PUBLIC_` prefix is present

**Test Token:**
```bash
# Should return 200 OK
curl "https://api.mapbox.com/styles/v1/mapbox/streets-v12?access_token=YOUR_TOKEN"
```

### Issue: Authentication Not Working

**Symptoms:** Can't log in, redirected back to login

**Solutions:**
1. Check Firebase config in `.env.local`
2. Verify Firebase project has Auth enabled
3. Check authorized domains in Firebase Console
4. Add `localhost` to authorized domains

**Debug:**
```javascript
// Check Firebase initialization
console.log(auth); // Should not be null
```

### Issue: API Requests Failing

**Symptoms:** No data loading, 404/500 errors

**Solutions:**
1. Verify backend is running: `curl http://localhost:8000/events`
2. Check `NEXT_PUBLIC_API_URL` in `.env.local`
3. Check browser Network tab for CORS errors
4. Verify backend CORS settings

**Test Backend:**
```bash
# Should return events JSON
curl http://localhost:8000/events
```

### Issue: Build Errors

**Symptoms:** `npm run build` fails

**Solutions:**
1. Clear Next.js cache:
   ```bash
   rm -rf .next
   npm run build
   ```

2. Reinstall dependencies:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

3. Check Node version:
   ```bash
   node --version  # Should be 18+
   ```

### Issue: TypeScript Errors

**Symptoms:** Red squiggly lines, type errors

**Solutions:**
1. These are expected before `npm install`
2. After install, restart VS Code
3. Check tsconfig.json exists
4. Run: `npm run lint`

### Issue: Styles Not Applied

**Symptoms:** Unstyled components, no CSS

**Solutions:**
1. Check Tailwind is configured: `tailwind.config.js` exists
2. Verify PostCSS config: `postcss.config.js` exists
3. Check globals.css is imported in layout.tsx
4. Restart dev server

---

## Post-Deployment Checklist

- [ ] All environment variables set in production
- [ ] Firebase authorized domains updated
- [ ] Backend CORS allows production domain
- [ ] Mapbox token has correct permissions
- [ ] SSL certificate installed (HTTPS)
- [ ] Analytics tracking enabled
- [ ] Error logging configured
- [ ] Performance monitoring setup

---

## Performance Optimization

### 1. Image Optimization
```tsx
// Use Next.js Image component
import Image from 'next/image';

<Image
  src={event.media_urls[0]}
  alt="Event"
  width={300}
  height={200}
  loading="lazy"
/>
```

### 2. Code Splitting
```tsx
// Dynamic imports for heavy components
const MapView = dynamic(() => import('@/components/map/map-view'), {
  ssr: false,
  loading: () => <LoadingSpinner />
});
```

### 3. Caching Strategy
```typescript
// Adjust React Query staleTime
useQuery({
  queryKey: ['events'],
  queryFn: getEvents,
  staleTime: 5 * 60 * 1000, // 5 minutes
});
```

---

## Next Steps

1. **Add Report Form Component** - Full implementation with media upload
2. **Implement Subscriptions UI** - Draw areas on map, manage alerts
3. **Add Real-Time Updates** - WebSocket integration
4. **Enhance Analytics** - More charts and insights
5. **Add Tests** - Unit and integration tests
6. **PWA Setup** - Make it a Progressive Web App
7. **i18n Support** - Multi-language support

---

## Support & Resources

- **Documentation:** [Next.js Docs](https://nextjs.org/docs)
- **Mapbox GL JS:** [Documentation](https://docs.mapbox.com/mapbox-gl-js/)
- **Firebase:** [Documentation](https://firebase.google.com/docs)
- **Tailwind CSS:** [Documentation](https://tailwindcss.com/docs)
- **React Query:** [Documentation](https://tanstack.com/query/latest)

---

## 🎉 Congratulations!

Your SmartCitySense frontend is now fully set up and ready for development! The system should be:

✅ Displaying real-time city events on an interactive map
✅ Showing analytics and trends
✅ Processing user authentication
✅ Connecting to backend APIs
✅ Visualizing sentiment data
✅ Responsive and beautiful

Happy coding! 🚀
