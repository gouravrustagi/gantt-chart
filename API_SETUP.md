# API Key Setup Guide

## Default API Keys

The app comes with these pre-configured API keys in `config.py`:

1. **DEMO-KEY-12345** - Demo/testing key
2. **YOUR-CUSTOM-KEY-HERE** - Replace with your own
3. **MOBILE-APP-KEY-2026** - For mobile access

## How to Add Your Own API Keys

### Method 1: Edit config.py
Open `config.py` and add your keys to the list:
```python
VALID_API_KEYS = [
    "YOUR-SECRET-KEY-123",
    "ANOTHER-KEY-456",
    "TEAM-KEY-789"
]
```

### Method 2: Use Environment Variable
Set an environment variable:

**Windows (PowerShell):**
```powershell
$env:GANTT_API_KEY="YOUR-SECRET-KEY"
python app.py
```

**Linux/Mac:**
```bash
export GANTT_API_KEY="YOUR-SECRET-KEY"
python app.py
```

## Security Features

✅ All endpoints require valid API key
✅ Keys stored in session after login
✅ Logout functionality to clear session
✅ 401 error for invalid keys
✅ Password-masked input field

## Using the App

1. **Start the server:**
   ```bash
   python app.py
   ```

2. **Open in browser:**
   - Desktop: http://localhost:5000
   - Mobile: http://YOUR_IP:5000

3. **Login with API key:**
   - Enter one of the valid API keys
   - Click "Verify & Login"
   - Demo key: `DEMO-KEY-12345`

4. **Logout:**
   - Click the logout button in the header
   - Requires re-authentication

## Best Practices

🔒 **Never commit real API keys to version control**
🔑 Use strong, random keys for production
👥 Create different keys for different users/teams
🔄 Rotate keys regularly
📝 Keep a secure backup of your keys
