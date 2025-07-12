#!/bin/bash
set -e

echo "🚀 Starting Vilcos deployment process..."

# 0. Force rebuild to ensure latest template changes
echo "Step 0: Force rebuilding templates..."
./force-rebuild.sh

# 1. Generate optimized static files
echo "Step 1: Building optimized site..."
./vilcos publish

# 2. Deploy to Fly.io
echo "Step 2: Deploying to Fly.io..."
cd public && fly deploy --local-only

echo "✅ Deployment complete! Your site should be live in a few moments."
echo "   Visit your site at: https://$(grep 'app =' fly.toml | cut -d"'" -f2).fly.dev" 