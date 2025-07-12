#!/bin/bash

# ANSI color codes for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Display banner
echo -e "${BLUE}"
echo "╔═════════════════════════════════════════════════════════════╗"
echo "║           VILCOS STATIC WEBSITE PUBLISHER                   ║"
echo "║                Production Deployment                        ║"
echo "╚═════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Default publish directory
PUBLISH_DIR="${1:-./public}"

# Make sure public directory exists first
mkdir -p "$PUBLISH_DIR"

# Now make it absolute
PUBLISH_DIR=$(realpath "$PUBLISH_DIR")
BASE_URL="${2:-http://localhost}"

# Ensure npm is installed
if ! command -v npm &> /dev/null; then
  echo -e "${RED}Error: npm is required but not found${NC}"
  exit 1
fi

# Check if we're in the right directory (should have package.json)
if [ ! -f "package.json" ]; then
  echo -e "${RED}Error: package.json not found. Are you in the Vilcos directory?${NC}"
  exit 1
fi

# Create a post-processing script if it doesn't exist
if [ ! -f "./post-process.js" ]; then
  echo -e "${YELLOW}Creating post-processing script...${NC}"
  cat > ./post-process.js << 'EOL'
import { processHtmlFiles, createRobotsTxt, generateSitemap } from './publish-functions.js';
import path from 'path';

// Get the publish directory from command line args
const publishDir = process.argv[2];
const baseUrl = process.argv[3] || 'http://localhost';

if (!publishDir) {
  console.error('Error: No publish directory specified');
  process.exit(1);
}

console.log(`Post-processing website in: ${publishDir}`);

// Run all optimization tasks
processHtmlFiles(publishDir);
createRobotsTxt(publishDir, true);
generateSitemap(publishDir, baseUrl);

console.log('Post-processing complete!');
EOL
fi

# Build the frontend assets
echo -e "${YELLOW}Building optimized frontend assets...${NC}"
npm run build

if [ ! -d "templates/dist" ]; then
  echo -e "${RED}Error: Build failed or templates/dist directory is missing${NC}"
  exit 1
fi

# Create the publishing directory
echo -e "${YELLOW}Creating publishing directory: $PUBLISH_DIR${NC}"
mkdir -p "$PUBLISH_DIR"

# Copy all built assets to the publishing directory
echo -e "${YELLOW}Copying optimized assets to publishing directory...${NC}"
cp -r templates/dist/* "$PUBLISH_DIR/"
if [ -d "templates/dist/assets" ]; then
  cp -r templates/dist/assets "$PUBLISH_DIR/"
fi

# Run post-processing with Node.js
echo -e "${YELLOW}Running post-processing optimizations...${NC}"
node ./post-process.js "$PUBLISH_DIR" "$BASE_URL"

# Create a Caddyfile for serving the static site
echo -e "${YELLOW}Creating Caddyfile for production...${NC}"
cat > "${PUBLISH_DIR}/Caddyfile" << 'EOL'
:80 {
  root * /srv
  file_server
  
  # Enable compression
  encode gzip zstd
  
  # Security headers
  header {
    # Enable strict transport security
    Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
    # Enable cross-site filter protection
    X-XSS-Protection "1; mode=block"
    # Prevent MIME sniffing
    X-Content-Type-Options "nosniff"
    # Restrict embedding
    X-Frame-Options "SAMEORIGIN"
    # Content security policy
    Content-Security-Policy "default-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' https://images.unsplash.com https://randomuser.me data:; frame-src 'self' https://www.youtube.com; child-src 'self' https://www.youtube.com; script-src 'self' https://www.googletagmanager.com 'unsafe-inline';"
  }
}
EOL

# Create a docker-compose file for production deployment
echo -e "${YELLOW}Creating Docker Compose for production...${NC}"
cat > "${PUBLISH_DIR}/compose.yaml" << EOL
services:
  caddy:
    image: caddy:2-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - .:/srv
      - caddy_data:/data
      - caddy_config:/config
    environment:
      - SITE_ROOT=/srv
    restart: unless-stopped

volumes:
  caddy_data:
  caddy_config:
EOL

# Create a deployment guide
echo -e "${YELLOW}Creating deployment instructions...${NC}"
cat > "${PUBLISH_DIR}/DEPLOY.md" << EOL
# Vilcos Static Website Deployment

This directory contains a production-ready static website built with Vilcos.

## Quick Deployment

The simplest way to deploy is using Docker with the provided compose.yaml:

\`\`\`bash
docker compose up -d
\`\`\`

This will start a Caddy server hosting your site at http://localhost.

## Manual Deployment

If you prefer to use your own web server:

1. Configure your web server to serve the files in this directory
2. The main website entry point is index.html at the root
3. Set appropriate caching headers for assets/ directory

## Customization

- Edit the Caddyfile to customize server settings
- Modify compose.yaml to change ports or add domains

## Security

The included Caddyfile sets up secure headers by default. Review them to ensure they match your security requirements.
EOL

# Add timestamp to show when the site was published
echo -e "${YELLOW}Adding publishing information...${NC}"
PUBLISH_DATE=$(date)
cat > "${PUBLISH_DIR}/VERSION.txt" << EOL
Vilcos Static Website
Published: $PUBLISH_DATE
Base URL: $BASE_URL
EOL

# Create a Dockerfile for Fly.io deployment
echo -e "${YELLOW}Creating Fly.io deployment files...${NC}"
cat > "${PUBLISH_DIR}/Dockerfile" << 'EOL'
FROM caddy:2-alpine

WORKDIR /srv

# Copy everything from the current directory
COPY . /srv/

# Move the Caddyfile to the correct location
RUN mv /srv/Caddyfile /etc/caddy/Caddyfile

# Set proper permissions
RUN chmod -R 755 /srv

# Expose HTTP port
EXPOSE 80
EOL

# Create a fly.toml template
cat > "${PUBLISH_DIR}/fly.toml" << EOL
app = "vilcos-site"
primary_region = "iad"

[build]
  dockerfile = "Dockerfile"

[http_service]
  internal_port = 80
  force_https = true
  auto_stop_machines = "stop"
  auto_start_machines = true
  min_machines_running = 0
  processes = ["app"]

  [[http_service.checks]]
    interval = "30s"
    timeout = "5s"
    grace_period = "10s"
    method = "GET"
    path = "/"

[[vm]]
  memory = "1gb"
  cpu_kind = "shared"
  cpus = 1
EOL

echo -e "${GREEN}✓ Static site published successfully to: ${PUBLISH_DIR}${NC}"
echo -e "${BLUE}➤ To deploy, navigate to that directory and run:${NC}"
echo -e "${YELLOW}   cd \"$PUBLISH_DIR\" && docker compose up -d${NC}"
echo -e "${BLUE}➤ Your site will be available at:${NC} $BASE_URL"
echo -e "${BLUE}➤ For more deployment options, see:${NC} $PUBLISH_DIR/DEPLOY.md" 