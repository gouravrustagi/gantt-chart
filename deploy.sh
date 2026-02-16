#!/bin/bash

echo "🚀 Deploying to Vercel..."

# Install Vercel CLI if not installed
if ! command -v vercel &> /dev/null
then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
fi

# Login to Vercel
echo "🔐 Please login to Vercel..."
vercel login

# Deploy
echo "🌐 Deploying application..."
vercel --prod

echo "✅ Deployment complete!"
echo "📱 Your app is now live!"
