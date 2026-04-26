# Comprehensive DevOps Lab Manual: Build & Deploy Plan

This document provides a complete, step-by-step guide to setting up, building, and deploying the DevOps Learning Lab. It covers everything from local environment preparation to container orchestration.

---

## Phase 0: Local Environment Setup

Before building containers, it's best practice to ensure your local environment can run the code for development and linting.

1. **Install Python Dependencies**

   Run this command to install the necessary libraries locally:

   ```powershell
   pip install -r app/requirements.txt
   ```

2. **Verify Local App (Optional)**

   You can test if the app starts locally (it will report a Redis connection error, which is expected):

   ```powershell
   python app/app.py
   ```

---

## Phase 1: Project Structure & File Glossary

Here is the complete list of files in this project and their specific roles in the DevOps lifecycle:

### Core Application (Python/Flask)

- **[app/app.py](file:///c:/Users/Gaurav%20Sahu/.gemini/antigravity/scratch/devops-learning-lab/app/app.py)**: The main web application logic with visit tracking.
- **[app/requirements.txt](file:///c:/Users/Gaurav%20Sahu/.gemini/antigravity/scratch/devops-learning-lab/app/requirements.txt)**: Lists the Python packages (`flask`, `redis`) required for the app.

### Containerization (Docker)

- **[Dockerfile](file:///c:/Users/Gaurav%20Sahu/.gemini/antigravity/scratch/devops-learning-lab/Dockerfile)**: Instructions for building the secure, multi-stage production image.
- **[.dockerignore](file:///c:/Users/Gaurav%20Sahu/.gemini/antigravity/scratch/devops-learning-lab/.dockerignore)**: Prevents local junk files (like `__pycache__`) from entering the image.

### Orchestration (Docker Compose)

- **[docker-compose.yml](file:///c:/Users/Gaurav%20Sahu/.gemini/antigravity/scratch/devops-learning-lab/docker-compose.yml)**: Manages the 'web' and 'redis' services together locally.

### Kubernetes Manifests (Production Prep)

- **[k8s/app-deployment.yaml](file:///c:/Users/Gaurav%20Sahu/.gemini/antigravity/scratch/devops-learning-lab/k8s/app-deployment.yaml)**: Defines how the Flask app runs in a cluster (replicas, resources).
- **[k8s/redis-deployment.yaml](file:///c:/Users/Gaurav%20Sahu/.gemini/antigravity/scratch/devops-learning-lab/k8s/redis-deployment.yaml)**: Defines the Redis backend in Kubernetes.
- **[k8s/services.yaml](file:///c:/Users/Gaurav%20Sahu/.gemini/antigravity/scratch/devops-learning-lab/k8s/services.yaml)**: Handles internal networking and external access (LoadBalancer) in Kubernetes.

### CI/CD & Documentation

- **[.github/workflows/main.yml](file:///c:/Users/Gaurav%20Sahu/.gemini/antigravity/scratch/devops-learning-lab/.github/workflows/main.yml)**: Automated pipeline for testing and building on every code push.
- **[README.md](file:///c:/Users/Gaurav%20Sahu/.gemini/antigravity/scratch/devops-learning-lab/README.md)**: High-level project documentation.
- **[docs/explanation.md](file:///c:/Users/Gaurav%20Sahu/.gemini/antigravity/scratch/devops-learning-lab/docs/explanation.md)**: Deep dive into DevOps concepts used here.

---

## Deep Dive: Understanding Image Naming & Versioning

You asked about where the name and version `1.0.0` come from. In DevOps, this is called **Image Tagging**.

### 1. Where is it named?

In this project, we define the image name in **[docker-compose.yml](file:///c:/Users/Gaurav%20Sahu/.gemini/antigravity/scratch/devops-learning-lab/docker-compose.yml)**:

```yaml
services:
  web:
    image: devops-lab-app:1.0.0  # <--- NAME : VERSION (TAG)
```

- **Name**: `devops-lab-app` is the identifier for your application.
- **Tag (Version)**: `1.0.0` is the version. If you change your code and want to release "Version 2", you would change this to `2.0.0`.

### 2. How does Kubernetes find it?

The Kubernetes manifest **[k8s/app-deployment.yaml](file:///c:/Users/Gaurav%20Sahu/.gemini/antigravity/scratch/devops-learning-lab/k8s/app-deployment.yaml)** is configured to look for this exact name and version:

```yaml
spec:
  containers:
  - name: flask-app
    image: devops-lab-app:1.0.0  # <--- MUST MATCH DOCKER NAME
```

### 3. Where is it stored?

- **Local Storage**: When you run `docker-compose build`, the image is stored in your computer's **Local Docker Registry**.
- **Remote Registry (Optional)**: In a real production environment, you would use `docker push` to send it to a cloud registry (like Docker Hub or Azure ACR) so that Kubernetes nodes can download it.

---

## Phase 2: Build Phase (Containerization)

In this phase, we package the application into a standard Docker image.

1. **Build the image**

   This command reads the `docker-compose.yml` and builds the image with the name/tag we specified:

   ```powershell
   docker-compose build
   ```

2. **Verify the built image**

   Check your local registry to see the newly created image and its version:

   ```powershell
   docker images | Select-String "devops-lab"
   ```

   *Expected Output: `devops-lab-app   1.0.0   [IMAGE_ID]   [SIZE]`*

---

## Phase 3: Deployment Phase (Orchestration)

Now we launch the entire stack (App + Database) using Docker Compose.

1. **Start the services in the background**

   ```powershell
   docker-compose up -d
   ```

2. **Check the status of the containers**

   ```powershell
   docker-compose ps
   ```

---

## Phase 4: Verification Phase (Testing)

Ensure everything is working correctly.

1. **Check Application Logs**

   Confirm the Flask app connected to Redis:

   ```powershell
   docker-compose logs web
   ```

2. **Test the Endpoint (CLI)**

   ```powershell
   curl http://localhost:5000
   ```

3. **Manual Browser Test**

   Open your browser and go to: `http://localhost:5000`

---

## Phase 5: Kubernetes Dry-Run (Advanced)

Before actually deploying to a cluster, verify your manifests are syntactically correct.

1. **Validate Deployment YAMLs**

   ```powershell
   kubectl apply -f k8s/ --dry-run=client
   ```

---

## Phase 7: Automation (GitHub Actions)

In a real-world project, you don't build and deploy manually every time. We use **GitHub Actions** to automate this entire process. This is defined in **[.github/workflows/main.yml](file:///c:/Users/Gaurav%20Sahu/.gemini/antigravity/scratch/devops-learning-lab/.github/workflows/main.yml)**.

### How the Automation Works

The workflow is divided into three sequential "Jobs". Each job must pass before the next one starts:

1. **Job 1: Security & Linting** (`security-and-lint`)
   - **Bandit**: Scans your Python code for security flaws (SAST).
   - **Hadolint**: Checks your Dockerfile for production best practices.
   - **Gitleaks**: Ensures no secrets (passwords/keys) are committed.

2. **Job 2: Build & Vulnerability Scan** (`build-and-scan`)
   - **Docker Build**: Builds the image automatically in the cloud.
   - **Trivy Scan**: Scans the actual Docker image for "CVEs" (known security vulnerabilities in the OS or libraries).
   - **Versioning**: Uses the **Commit SHA** (e.g., `devops-lab-app:a1b2c3d`) for unique, traceable versions.

3. **Job 3: Simulated Deployment** (`deploy-mock`)
   - If all tests and scans pass, it simulates a `kubectl apply` to your Kubernetes cluster.

### 🛡️ Real-World Case Study: "The Security Gauntlet"

During the development of this lab, we encountered and fixed three real-world security blockers that the pipeline caught:

| Tool | Finding | The Fix (Hardening) |
| :--- | :--- | :--- |
| **Bandit** | `B104`: Hardcoded bind to all interfaces (`0.0.0.0`) | Added `# nosec` to acknowledge intentional binding for container access. |
| **Hadolint** | `DL3013`: Pin versions in pip | Added `# hadolint ignore=DL3013` because we specifically want the **latest** build tools to pull in security patches. |
| **Trivy** | `HIGH` Vulnerability in `wheel` & `setuptools` | Added `RUN pip install --upgrade pip setuptools wheel` to **both** stages of the Dockerfile to overwrite vulnerable system libraries. |

### How to trigger it

Simply commit your code and push it to GitHub:

```powershell
# Stage all changes
git add .
# Commit with a descriptive message
git commit -m "Security: hardening build tools to pass Trivy scans"
# Push to the master branch
git push origin master
```

*You can then see the progress under the **"Actions"** tab on your GitHub repository page.*

---

## Phase 8: Cleanup

To stop and remove all containers and networks created by this lab:

1. **Shut down the lab**

   ```powershell
   docker-compose down
   ```

---

## Appendix A: Project Lifecycle Summary (The 6-Step Flow)

To summarize, here is the exact logical sequence we followed to build and secure this DevOps Learning Lab. This is how you "setup" a professional project from scratch:

### Step 1: Build the Application (Local Development)

- **What**: Write the Python code in `app/app.py`.
- **How**: Install dependencies with `pip install -r app/requirements.txt`.
- **Why**: You always start with a working application before trying to containerize it.

### Step 2: Run & Check (Local Verification)

- **What**: Test the app manually using `python app/app.py`.
- **How**: Check for syntax errors or logic flaws.
- **Why**: "Run Check #1" ensures your core code is stable.

### Step 3: Create Docker Image (Containerization)

- **What**: Write the `Dockerfile` and `docker-compose.yml`.
- **How**: Use `docker-compose build` to bundle your app into an image named `devops-lab-app:1.0.0`.
- **Why**: This makes your app "portable" so it runs the same on any machine.

### Step 4: Run & Check (Container Verification)

- **What**: Launch the services with `docker-compose up -d`.
- **How**: Use `docker-compose logs` and visit `http://localhost:5000`.
- **Why**: "Run Check #2" verifies that your app can communicate with other services (like Redis) inside a network.

### Step 5: Kubernetes Preparation (Orchestration)

- **What**: Define the desired state in `k8s/` (Deployments and Services).
- **How**: Use `kubectl apply --dry-run=client` to validate the YAML manifests.
- **Why**: This prepares your app for high-availability production environments.

### Step 6: GitHub Pipeline Setup (Automation)

- **What**: Create the `.github/workflows/main.yml` file.
- **How**: GitHub automatically detects any YAML file in the `.github/workflows/` folder and starts the "Actions" runner.
- **Why**: This final step automates all the "Run Checks" and "Builds" every time you push code, ensuring your project is always "green" and secure.
