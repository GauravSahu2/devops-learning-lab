# FILE SUMMARY:
# This Dockerfile uses a Multi-Stage build to create a small, secure, and production-ready
# image for the Flask application. Stage 1 installs dependencies, and Stage 2
# packages the app with a non-root user for security hardening.

# --- Stage 1: Build ---
# Use a lightweight Python 3.11 image as the starting point for building
FROM python:3.11-slim AS builder

# Create and enter a directory named '/build' inside the container
WORKDIR /build

# Install essential Python build tools
# Upgrade pip, setuptools, and wheel to the latest versions to fix security bugs
# hadolint ignore=DL3013
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy the dependency list from your local computer into the container
COPY app/requirements.txt .

# Install the application's libraries into a specific folder named '/install'
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Stage 2: Production ---
# Start again from a clean, small Python image for the final product
FROM python:3.11-slim

# Fix security vulnerabilities in the base image's pre-installed tools
# This ensures that even the system tools are up-to-date and secure
# hadolint ignore=DL3013
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Update the system's package list and install 'curl' for health checks
# Also create a new user named 'devopsuser' so we don't run as root (Admin)
# hadolint ignore=DL3008
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    useradd -m devopsuser && \
    rm -rf /var/lib/apt/lists/*

# Create and enter the '/app' directory where the code will live
WORKDIR /app

# Take the installed libraries from the 'builder' stage and move them here
# This keeps the final image small because it doesn't contain build tools
COPY --from=builder /install /usr/local

# Copy your actual Flask application code into the current directory (/app)
COPY app/ .

# Change the ownership of the /app folder to the 'devopsuser' we created
# This is a security best practice to limit file permissions
RUN chown -R devopsuser:devopsuser /app

# Switch the container's execution context to the 'devopsuser'
# All following commands and the app itself will run with limited privileges
USER devopsuser

# Document that this container is designed to listen on network port 5000
EXPOSE 5000

# Set up an automatic health check that runs every 30 seconds
# It uses 'curl' to see if the web server is actually responding
# We use the new /health endpoint to avoid incrementing the visit counter
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:5000/health || exit 1

# Specify the command to start your Flask application
# This is the 'entrypoint' that runs when the container starts up
CMD ["python", "app.py"]



