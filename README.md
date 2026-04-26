# DevOps Learning Lab 🚀

Welcome to the **DevOps Learning Lab**! This project is designed to help you practice building, containerizing, and orchestrating a multi-container application with a focus on **Security (DevSecOps)**.

---

## 🏗️ Architecture

- **App**: Python Flask Web Server.
- **Cache**: Redis (Alpine-based).
- **CI/CD**: GitHub Actions with Security gates (Bandit, Hadolint, Trivy, Gitleaks).
- **Orchestration**: Kubernetes (Deployments & Services).

---

## 🛠️ Setup & Running Locally

### 1. Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed.
- (Optional) [Minikube](https://minikube.sigs.k8s.io/docs/start/) or Docker Desktop's Kubernetes enabled.

### 2. Run with Docker Compose

To start the application locally:

```bash
docker-compose up --build
```

- Open `http://localhost:5000` in your browser.
- You should see the visitor count incrementing!

---

## ☸️ Kubernetes Deployment

### 1. Build the image for K8s

```bash
docker build -t devops-lab-app:latest .
```

### 2. Apply Manifests

```bash
kubectl apply -f k8s/
```

### 3. Verify

```bash
kubectl get pods
kubectl get svc
```

Access the app via the `flask-service` external IP (or `minikube service flask-service`).

---

## 🛡️ Security Tools Used

- **Bandit**: Scans Python code for security issues.
- **Hadolint**: Lints Dockerfile for best practices.
- **Trivy**: Scans container images for vulnerabilities.
- **Gitleaks**: Detects hardcoded secrets in the repo.

---

## 📚 Learning Resources

- Check [docs/explanation.md](docs/explanation.md) for a line-by-line breakdown of every file!
- Follow the [CI/CD pipeline](.github/workflows/main.yml) to see how automation works.
