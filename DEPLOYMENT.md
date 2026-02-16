# Deployment Guide

## Deploy to Vercel

### Prerequisites
- Install Vercel CLI: `npm install -g vercel`
- Create account at https://vercel.com

### Steps
1. **Login to Vercel**
   ```bash
   vercel login
   ```

2. **Deploy**
   ```bash
   cd "c:\Users\goura\OneDrive\Desktop\new app"
   vercel
   ```

3. **Follow prompts:**
   - Set up and deploy? Yes
   - Which scope? Your account
   - Link to existing project? No
   - Project name: gantt-chart-generator
   - Directory: ./
   - Override settings? No

4. **Production Deploy**
   ```bash
   vercel --prod
   ```

Your app will be live at: `https://gantt-chart-generator.vercel.app`

---

## Generate Android APK

### Method 1: PWA Builder (Easiest)
1. Visit https://www.pwabuilder.com/
2. Enter your Vercel URL: `https://your-app.vercel.app`
3. Click "Start"
4. Click "Package For Stores"
5. Select "Android"
6. Download APK
7. Install on Android device

### Method 2: Capacitor (Professional)
1. **Install Capacitor**
   ```bash
   npm install -g @capacitor/cli
   npm install -g @capacitor/core @capacitor/android
   ```

2. **Initialize**
   ```bash
   cd "c:\Users\goura\OneDrive\Desktop\new app"
   npm init -y
   npx cap init "Gantt Chart" "com.ganttchart.app" --web-dir=templates
   ```

3. **Add Android Platform**
   ```bash
   npx cap add android
   ```

4. **Configure**
   - Edit `capacitor.config.json`:
   ```json
   {
     "appId": "com.ganttchart.app",
     "appName": "Gantt Chart",
     "webDir": "templates",
     "server": {
       "url": "https://your-vercel-url.vercel.app",
       "cleartext": true
     }
   }
   ```

5. **Build APK**
   ```bash
   npx cap sync
   npx cap open android
   ```
   - In Android Studio: Build > Build Bundle(s) / APK(s) > Build APK

### Method 3: Using PWA Features (Simplest)
Your app is already a PWA! Users can:
1. Open the Vercel URL in Chrome on Android
2. Tap menu (⋮) > "Install app" or "Add to Home Screen"
3. The app installs like a native app (no APK needed!)

---

## Environment Variables

For production on Vercel, add environment variables:
1. Go to Vercel Dashboard
2. Project Settings > Environment Variables
3. Add any sensitive keys (e.g., API keys)

---

## Custom Domain (Optional)

1. Vercel Dashboard > Project > Settings > Domains
2. Add your custom domain
3. Update DNS records as instructed

---

## Updates

To update the deployed app:
```bash
git add .
git commit -m "Update"
vercel --prod
```

Or push to GitHub and enable Vercel auto-deployment.
