# CI/CD with Jenkins + Kubernetes + Argo CD: Advanced Deployment Strategies

A comprehensive CI/CD pipeline demonstrating advanced DevOps practices with **Jenkins**, **Kubernetes**, and **Argo CD**, featuring three distinct deployment strategies: **Standard Rolling Updates**, **Blue-Green**, and **Canary** deployments using **Argo Rollouts**.

## 🎯 Overview

This project showcases modern **DevOps best practices** including:
- **Docker-in-Docker (DinD)** containerized builds
- **GitOps workflow** with automated manifest management
- **Multi-strategy Kubernetes deployments** with Argo Rollouts
- **Infrastructure as Code** approach
- **Zero-downtime deployments** and **progressive delivery**

> **📝 Important Note**: The Kubernetes Ingress configurations in this project are designed for **KinD (Kubernetes in Docker)** with `extraPortMapping` feature enabled. For production Kubernetes environments, you'll need to configure your **Ingress Controller** or **Load Balancer** accordingly. Adjust the ingress rules and service types based on your cluster setup.

## 🏗️ Architecture & CI/CD Flow

```
┌─────────────────┐
│   Developer     │
│                 │
│  1. Git Push    │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│      Jenkins    │      │ Docker-in-Docker │      │   Docker Hub    │
│                 │      │                  │      │                 │
│ 2. CI Pipeline  │─────▶│  3. Build & Test │─────▶│ 4. Push Image   │
│   - Checkout    │      │   - Docker Build │      │   (Git SHA Tag) │
│   - Test        │      │   - Run Tests    │      │                 │
└─────────┬───────┘      └──────────────────┘      └─────────────────┘
          │
          ▼
┌─────────────────┐
│  5. GitOps      │
│ Update Manifest │
│  - Update YAML  │
│  - Git Commit   │
│  - Git Push     │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐      ┌─────────────────────────────────────────┐
│    Argo CD      │      │             Kubernetes                  │
│                 │      │                                         │
│ 6. Sync & Deploy│─────▶│ 7. Deployment Strategy Execution       │
│  - Detect Change│      │   ┌─────────────┐ ┌─────────────────┐   │
│  - Pull Manifest│      │   │  Standard   │ │   Blue-Green    │   │
│  - Apply to K8s │      │   │   Rolling   │ │    Rollout      │   │
└─────────────────┘      │   │   Update    │ │  (Argo Rollouts)│   │
                         │   └─────────────┘ └─────────────────┘   │
                         │   ┌─────────────────┐                   │
                         │   │     Canary      │                   │
                         │   │     Rollout     │                   │
                         │   │ (Argo Rollouts) │                   │
                         │   └─────────────────┘                   │
                         └─────────────────────────────────────────┘

CI/CD Pipeline Steps:
1. Developer pushes code to Git repository
2. Jenkins detects changes and starts CI pipeline
3. Docker-in-Docker builds container image and runs tests
4. Built image pushed to Docker Hub with Git SHA tag
5. Jenkins updates Kubernetes manifests with new image tag
6. Argo CD detects manifest changes and synchronizes
7. Selected deployment strategy executes in Kubernetes cluster
```

## 🚀 Key DevOps Technologies

### 🐳 **Docker-in-Docker (DinD)**
- Containerized build environment within Jenkins
- Isolated Docker builds without Docker socket binding
- Enhanced security and portability

### 📋 **GitOps Workflow**
- Declarative configuration management
- Git as single source of truth for infrastructure
- Automated manifest updates via CI pipeline

### 🎯 **Argo CD Integration**
- Continuous deployment automation
- Declarative GitOps deployments
- Real-time synchronization with Git repository

### ⚙️ **Advanced Deployment Strategies**
- **Argo Rollouts** for sophisticated deployment patterns
- **Traffic management** and **progressive delivery**
- **Automated rollback capabilities**

## 📋 Deployment Strategies

This project demonstrates **three distinct deployment strategies**, each optimized for different operational requirements:

### 🔄 **Standard Rolling Updates**
- **Traditional Kubernetes deployments**
- Sequential pod replacement
- Built-in Kubernetes functionality
- **Use case**: Development environments, simple applications

### 🔵🟢 **Blue-Green Deployment**
- **Zero-downtime deployments**
- Parallel environment maintenance (Blue ↔ Green)
- Instant traffic switching with immediate rollback
- **Use case**: Critical production systems requiring instant rollback

### 🐦 **Canary Deployment**
- **Progressive traffic shifting**: 25% → 50% → 75% → 100%
- **Risk mitigation** through gradual exposure
- **Automated progression** with health monitoring
- **Use case**: High-traffic applications, risk-sensitive deployments

## 📁 Infrastructure Layout

```
├── Dockerfile                      # Jenkins + Docker + kubectl image
├── docker-compose.yaml            # Jenkins + DinD orchestration
├── Jenkinsfile                     # Declarative CI/CD pipeline
├── app/                           # Test Flask application
│   ├── Dockerfile                 # Multi-stage container build
│   ├── app.py                     # Test app (deployment-aware)
│   ├── requirements.txt
│   └── tests/
└── manifests/                     # Kubernetes Infrastructure as Code
    ├── Deployment/                # Standard Kubernetes deployment
    ├── Rollout-BlueGreen/        # Blue-Green with Argo Rollouts
    └── Rollout-Canary/           # Canary with Argo Rollouts
```

## 🛠️ Prerequisites & Infrastructure

### Core Requirements
- **Docker & Docker Compose**
- **Kubernetes Cluster** (KinD recommended for local development)
- **Argo CD** (for GitOps continuous deployment)
- **Argo Rollouts** (for advanced deployment strategies)
- **NGINX Ingress Controller** (or equivalent)

### For KinD Setup (Recommended)
```bash
# KinD cluster with ingress support
cat <<EOF | kind create cluster --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
EOF
```

## 🚀 Quick Start

### 1. Infrastructure Setup

```bash
# Clone repository
git clone <your-repo-url>
cd CICD-Jenkins-K8S

# Launch Jenkins with Docker-in-Docker
docker-compose up -d

# Get Jenkins admin password
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

### 2. Kubernetes Environment

```bash
# Install Argo CD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Install Argo Rollouts
kubectl create namespace argo-rollouts
kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml

# Install NGINX Ingress (for KinD)
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Create application namespace
kubectl create namespace flask-app
```

### 3. Configure Deployment Strategy

configure `Jenkinsfile` to select deployment approach:

```groovy
environment {
    DEPLOYMENT_STRATEGY = "BlueGreen"  // Options: Standard, Canary, BlueGreen
}
```

### 4. Jenkins Configuration

**Required Jenkins Plugins:**
- Docker Pipeline
- Kubernetes CLI  
- SSH Agent
- Git

**Required Credentials:**
- `dockerhub-credentials`: Docker Hub authentication
- `github-id`: SSH private key for Git operations

## ⚙️ Pipeline Architecture

### Jenkins Pipeline Stages

1. **Checkout** - Source code retrieval
2. **Build** - Docker image creation with metadata injection
3. **Test** - Automated test execution in container
4. **Login** - Docker registry authentication  
5. **Push** - Image publication with Git SHA tagging
6. **Update Manifest** - GitOps manifest modification
7. **Commit & Push** - Infrastructure changes via Git


## 🎛️ Deployment Operations

### Blue-Green Strategy Management
```bash
# Monitor rollout status
kubectl argo rollouts get rollout flask-app-bluegreen -n flask-app --watch

# Promote new version (traffic switch)
kubectl argo rollouts promote flask-app-bluegreen -n flask-app

# Immediate rollback
kubectl argo rollouts undo flask-app-bluegreen -n flask-app
```

### Canary Strategy Management  
```bash
# Watch progressive deployment
kubectl argo rollouts get rollout flask-app-rollout -n flask-app --watch

# Manual progression control
kubectl argo rollouts promote flask-app-rollout -n flask-app

# Abort canary rollout
kubectl argo rollouts abort flask-app-rollout -n flask-app
```

## 📊 Monitoring & Observability

### Health Check Architecture
- **Liveness Probes**: Application health validation
- **Readiness Probes**: Traffic routing decisions  
- **Startup Probes**: Initial container health validation

## 🔐 Security & Best Practices

- **Non-root container execution**
- **Resource limits and requests**
- **Secure credential management** in Jenkins
- **SSH-based Git authentication**

## 🔧 Environment-Specific Configuration

### For Cloud Providers (AWS/GCP/Azure)
```yaml
# Use LoadBalancer service type
spec:
  type: LoadBalancer
```

### For On-Premises Clusters
```yaml
# Configure NodePort or use specific ingress controller
spec:
  type: NodePort
```

### For Minikube
```bash
# Enable ingress addon
minikube addons enable ingress
```

## 🚀 Advanced Features

### GitOps Best Practices
- **Declarative configuration management**
- **Git-based audit trail**
- **Automated drift detection**
- **Multi-environment support**

### Progressive Delivery
- **Traffic-based deployment validation**
- **Automated rollback triggers**
- **Canary analysis with metrics**
- **Blue-Green environment management**

## 📈 Production Considerations

- **Multi-cluster deployments**
- **Security scanning integration**
- **Monitoring and alerting**
- **Database migration strategies**
- **Secret management with external systems**

---
