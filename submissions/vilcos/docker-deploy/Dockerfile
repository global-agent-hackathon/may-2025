# Multi-stage Dockerfile for Vilcos
# Production-ready static website build using pre-built files

FROM caddy:2-alpine

WORKDIR /srv

# Copy the Caddyfile
COPY docker-deploy/Caddyfile /etc/caddy/Caddyfile

# Copy the entire public directory content (already optimized with analytics)
COPY public/ /srv/

# Set proper permissions
RUN chmod -R 755 /srv

# Expose HTTP port
EXPOSE 80 