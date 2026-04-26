# FILE SUMMARY:
# This Dockerfile uses a Multi-Stage build to create a small, secure, and production-ready
# image for the Flask application. Stage 1 installs dependencies, and Stage 2
# packages the app with a non-root user for security hardening.

# --- Stage 1: Build ---
# Use a lightweight Python base image for building
FROM python:3.11-slim AS builder

# Set the working directory for the build stage
WORKDIR /build

# Install dependencies to a local folder
# Upgrade pip and build tools to avoid known vulnerabilities
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
# Copy requirements file first to leverage Docker cache
COPY app/requirements.txt .
# Install dependencies into /install folder
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Stage 2: Production ---
# Start a fresh, clean stage to keep the final image small
FROM python:3.11-slim

# Install curl for the healthcheck and create a non-root user
# hadolint ignore=DL3008
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    useradd -m devopsuser && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory for the final application
WORKDIR /app

# Copy only the installed dependencies from the builder stage
# Transfer the binaries/libraries from the builder stage
COPY --from=builder /install /usr/local

# Copy the application code
# Copy the Flask app code into the container
COPY app/ .

# Change ownership to the non-root user
# Ensure the app files are owned by the non-root user
RUN chown -R devopsuser:devopsuser /app

# Switch to the non-root user
# Tell Docker to run all subsequent commands as 'devopsuser'
USER devopsuser

# Expose the application port
# Inform Docker that the container listens on port 5000
EXPOSE 5000

# Healthcheck to ensure the container is running correctly
# Check if the app is responding every 30 seconds
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:5000/ || exit 1

# Run the application
# Command to start the application
CMD ["python", "app.py"]



