FROM node:23-alpine AS build

WORKDIR /app

# Install curl with root privileges
RUN apk update && \
    apk add --no-cache curl bash

RUN adduser -D -h /home/adgenius adgenius && chown -R adgenius /app
USER adgenius
ENV PATH="/home/adgenius/.local/bin:${PATH}"

# Install bun
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/home/adgenius/.bun/bin:${PATH}"

# Define build argument for API URL
ARG VITE_API_URL=http://localhost:8000

# Set it as an environment variable
ENV VITE_API_URL=${VITE_API_URL}

COPY . .
RUN bun install
RUN bun run build

# The build output will be in /app/dist
