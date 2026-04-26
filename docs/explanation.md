# Deep Dive: How Everything Works 🧠

This document provides a line-by-line explanation of every file in the DevOps Learning Lab.

---

## 1. The Application (`app/app.py`)

This is our "Business Logic".

- `from flask import Flask`: Imports the web framework.
- `import redis`: Imports the library to talk to our Redis database.
- `os.getenv("REDIS_HOST", "localhost")`: Dynamically reads the Redis address. In Docker Compose/K8s, this is the **service name** (DNS).
- `cache.incr("hits")`: This is an **Atomic Operation**. Even if 1000 people click at once, Redis ensures the count is accurate.
- `socket.gethostname()`: Returns the ID of the container. In Kubernetes, this changes as you refresh if you have multiple replicas, showing **Load Balancing** in action.

---

## 2. The Dockerfile

This is the "Blueprint" for our container.

- `FROM python:3.11-slim as builder`: We use a **Multi-Stage Build**. Stage 1 installs dependencies.
- `RUN useradd -m devopsuser`: **Security Best Practice!** Never run containers as `root`. If an attacker breaks into the app, they won't have full system access.
- `COPY --from=builder /install /usr/local`: We only copy the *results* of the build, not the build tools themselves. This makes the image smaller and more secure (smaller attack surface).
- `HEALTHCHECK`: Tells Docker/K8s how to check if the app is *actually* working, not just "running".

---

## 3. Docker Compose (`docker-compose.yml`)

Local Orchestration.

- `services:`: Defines our two containers (`web` and `redis`).
- `depends_on:`: Tells Docker to start Redis *before* the web app.
- `networks:`: Creates an isolated virtual network where containers can talk to each other by name (e.g., `http://redis`).

---

## 4. Kubernetes Manifests (`k8s/`)

Production Orchestration.

- `replicas: 2`: Ensures 2 copies of your app are always running. If one crashes, K8s starts another one (**Self-Healing**).
- `resources: limits:`: Prevents a single container from consuming all the RAM/CPU of the server (**Noisy Neighbor** prevention).
- `type: LoadBalancer`: Requests an external IP address so the world can reach your app.

---

## 5. CI/CD Pipeline (`.github/workflows/main.yml`)

The "Assembly Line".

- `on: push`: Runs every time you save code to the `main` branch.
- `bandit`: Finds "bad" code (like using `eval()` or weak crypto).
- `hadolint`: Finds "bad" Docker habits (like using `latest` tags or not clearing cache).
- `trivy`: Scans the final image for known CVEs (vulnerabilities). **In the real world, you block the deploy if Trivy finds High/Critical issues.**

---

## 🔗 The "Connectivity" - How they talk to each other

### 1. How the Dockerfile connects to Compose

In `docker-compose.yml`, you see the line `build: .`.

- This tells Docker Compose: "Don't look for an image on the internet; instead, look in the current folder for a file named **Dockerfile** and build it."
- Once built, Compose names that image (e.g., `devops-learning-lab_web`) and starts a container from it.

### 2. How Docker Compose "Connects" Containers

In our Compose file, we have two services: `web` and `redis`.

- **The Secret Sauce**: Docker Compose creates a private virtual network (we named it `lab-network`).
- **Service Discovery**: Inside this network, Docker runs a small DNS server. When the `web` app asks for `redis`, Docker looks at the `lab-network` map and says, "Oh, Redis is at IP 172.18.0.2," and connects them automatically. This is why we use `REDIS_HOST=redis` in our code!

### 3. How Kubernetes Orchestrates Everything

Kubernetes is like a "Manager" that never sleeps.

- **Deployments**: These are the "Desired State." If you say `replicas: 2`, K8s constantly checks: "Are there 2 pods running?" If one container crashes, K8s immediately starts a new one.
- **Services (The Traffic Cop)**: Pods are temporary and their IP addresses change. A **Service** (like `flask-service`) provides a *permanent* IP or name. When the `web` pod wants Redis, it asks the `redis-service`. The Service then forwards that request to the actual Redis Pod.
- **Load Balancing**: Our `flask-service` is a `LoadBalancer`. It takes traffic from the internet and distributes it across all your running Flask Pods.

---

## 🚀 Key DevSecOps Concepts Demonstrated

1. **Infrastructure as Code (IaC)**: Docker and K8s files define our environment.
2. **Shift-Left Security**: We scan for bugs *before* the code is even built.
3. **Immutability**: Once a container image is built, it never changes. We just deploy new versions.
4. **Observability**: Health checks allow the system to monitor itself.

