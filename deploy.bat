@echo off
echo 🚀 Deploying to Vercel...

REM Check if Vercel CLI is installed
where vercel >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo 📦 Installing Vercel CLI...
    npm install -g vercel
)

REM Login to Vercel
echo 🔐 Please login to Vercel...
call vercel login

REM Deploy
echo 🌐 Deploying application...
call vercel --prod

echo ✅ Deployment complete!
echo 📱 Your app is now live!
pause
