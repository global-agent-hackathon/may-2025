#!/bin/bash
set -e

echo "🔄 Force rebuilding templates with latest changes..."

# Clear the templates/dist directory if it exists
if [ -d "templates/dist" ]; then
  rm -rf templates/dist
  echo "  Cleared templates/dist directory"
fi

# Run the build
echo "  Running build..."
npm run build

# Verify the build 
if [ -d "templates/dist" ] && [ -f "templates/dist/index.html" ]; then
  echo "✅ Template rebuild successful!"
else
  echo "❌ Template rebuild failed!"
  echo "  Looking for template in alternate locations..."
  find . -name "index.html" | grep -v "node_modules" | grep dist
  exit 1
fi

echo "🚀 Now run ./deploy.sh to deploy the latest changes" 