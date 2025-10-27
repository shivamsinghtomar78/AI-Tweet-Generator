#!/usr/bin/env bash
set -e

echo "==> Installing Python dependencies..."
pip install -r requirements.txt

echo "==> Checking Node.js version..."
node --version
npm --version

echo "==> Installing Node.js dependencies..."
cd frontend
npm install --legacy-peer-deps

echo "==> Building React frontend..."
npm run build

echo "==> Verifying build..."
if [ -d "build" ]; then
    echo "==> Build successful! Files:"
    ls -la build/
else
    echo "==> ERROR: Build directory not found!"
    exit 1
fi

cd ..
echo "==> Build complete!"
