# iOS Installation Guide

## Install on iPhone/iPad

### Method 1: Add to Home Screen (Recommended)

1. **Open Safari** on your iPhone/iPad
2. Go to your app URL: `https://your-app.vercel.app`
3. Tap the **Share button** (square with arrow pointing up) at the bottom
4. Scroll down and tap **"Add to Home Screen"**
5. Edit the name if desired (default: "Gantt Chart")
6. Tap **"Add"** in the top right corner
7. The app icon appears on your home screen!

### Features After Installation:
- ✅ Works like a native app
- ✅ Full-screen mode (no Safari UI)
- ✅ App icon on home screen
- ✅ Offline support
- ✅ Gemini API authentication
- ✅ All 10 chart types available
- ✅ Download charts as PNG

### Method 2: iOS App Store (Future)

To publish on the App Store:
1. Use **Capacitor** to wrap the PWA
2. Build with Xcode
3. Submit to App Store

**Steps:**
```bash
# Install Capacitor
npm install @capacitor/core @capacitor/cli @capacitor/ios

# Initialize
npx cap init "Gantt Chart" "com.ganttchart.app" --web-dir=templates

# Add iOS platform
npx cap add ios

# Configure server URL in capacitor.config.json
{
  "server": {
    "url": "https://your-vercel-url.vercel.app"
  }
}

# Open in Xcode
npx cap open ios
```

Then in Xcode:
- Select target device
- Build and run
- Archive for App Store submission

### Method 3: TestFlight (Beta Testing)

1. Build iOS app using Capacitor
2. Create App Store Connect account
3. Upload to TestFlight
4. Share TestFlight link with users
5. Users install via TestFlight app

### Compatibility:
- ✅ iOS 11.3+
- ✅ iPad OS 13+
- ✅ Safari only (for Add to Home Screen)
- ✅ All iPhone models
- ✅ Works on iPad

### Important iOS Notes:

**Service Worker Limitations:**
- iOS Safari has limited service worker support
- Offline mode works but may clear cache periodically
- Re-add to home screen if needed

**Display:**
- Opens in full-screen standalone mode
- No Safari browser UI
- Status bar matches app theme color

**Storage:**
- API key stored in session (re-login after app restart)
- Chart downloads save to Files app
- Limited to Safari's storage quota

### Troubleshooting:

**App not installing?**
- Make sure using Safari (not Chrome/Firefox)
- Clear Safari cache and try again
- Check iOS version (needs 11.3+)

**Can't find Share button?**
- Look at bottom of screen in Safari
- On iPad, it's at the top

**App not working offline?**
- Service workers cache on first visit
- Make sure you've opened the app online first
- iOS may clear cache - just reload once online

### User Instructions (Share with iPhone Users):

```
📱 Install Gantt Chart App on iPhone:

1. Open this link in Safari: [YOUR URL]
2. Tap the Share button (□↑) at bottom
3. Scroll and tap "Add to Home Screen"
4. Tap "Add" to install
5. Open from your home screen!

The app works offline and looks like a native app! 🎉
```

---

## Why This Works:

Your app is now a **Progressive Web App (PWA)** with:
- ✅ iOS-specific meta tags
- ✅ Apple Touch Icons (120, 152, 167, 180px)
- ✅ Standalone display mode
- ✅ iOS status bar styling
- ✅ Service worker for offline support
- ✅ Responsive design for all iOS devices

**No App Store required!** Users can install directly from Safari.
