# FILE SUMMARY:
# This Dockerfile uses a Multi-Stage build to create a small, secure, and production-ready
# image for the Flask application. Stage 1 installs dependencies, and Stage 2
# packages the app with a non-root user for security hardening.

# --- Stage 1: Build ---
# Use lightweight base image for building
FROM python:3.11-slim AS builder

# Set working directory for build stage
WORKDIR /build

# Upgrade build tools to fix security vulnerabilities
# hadolint ignore=DL3013
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements first for caching
COPY app/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Stage 2: Production ---
# Start fresh for final production image
FROM python:3.11-slim

# Fix system vulnerabilities by upgrading base tools
# hadolint ignore=DL3013
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install curl and create non-root user
# hadolint ignore=DL3008
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    useradd -m devopsuser && \
    rm -rf /var/lib/apt/lists/*

# Set production working directory
WORKDIR /app

# Transfer dependencies from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY app/ .

# Ensure non-root ownership
RUN chown -R devopsuser:devopsuser /app

# Switch to non-root security context
USER devopsuser

# Document application port
EXPOSE 5000

# Healthcheck using dedicated /health endpoint
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:5000/health || exit 1

# Command to start the application
CMD ["python", "app.py"]



