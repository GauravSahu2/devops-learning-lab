# FILE SUMMARY:
# This Dockerfile uses a Multi-Stage build to create a small, secure, and production-ready
# image for the Flask application. Stage 1 installs dependencies, and Stage 2
# packages the app with a non-root user for security hardening.

# --- Stage 1: Build ---
FROM python:3.11-slim AS builder # Use lightweight base image for building

WORKDIR /build # Set working directory for build stage

# hadolint ignore=DL3013
RUN pip install --no-cache-dir --upgrade pip setuptools wheel # Upgrade build tools

COPY app/requirements.txt . # Copy requirements first for caching

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt # Install deps

# --- Stage 2: Production ---
FROM python:3.11-slim # Start fresh for final production image

# hadolint ignore=DL3013
RUN pip install --no-cache-dir --upgrade pip setuptools wheel # Fix system vulnerabilities

# hadolint ignore=DL3008
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    useradd -m devopsuser && \
    rm -rf /var/lib/apt/lists/* # Install curl and create non-root user

WORKDIR /app # Set production working directory

COPY --from=builder /install /usr/local # Transfer dependencies from builder

COPY app/ . # Copy application code

RUN chown -R devopsuser:devopsuser /app # Ensure non-root ownership

USER devopsuser # Switch to non-root security context

EXPOSE 5000 # Document application port

# Healthcheck using dedicated /health endpoint
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:5000/health || exit 1

CMD ["python", "app.py"] # Command to start the application



