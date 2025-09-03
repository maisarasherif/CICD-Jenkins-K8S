# KinD (Kubernetes in Docker) Setup Guide

This guide provides detailed instructions for setting up this CI/CD project using KinD for local development and testing.

## 🐳 Why KinD?

KinD (Kubernetes in Docker) is perfect for:
- **Local development** and testing
- **CI/CD pipeline** testing
- **Learning Kubernetes** 
- **Reproducible environments**

## 📋 Prerequisites
**Docker**
**Kubectl**
**KinD**

## Cluster Configuration
### Standard Setup (For this project)

```bash
# Create cluster with required port mappings
cat <<EOF | kind create cluster --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 80      # Application HTTP
    hostPort: 80
    protocol: TCP
  - containerPort: 443     # Application HTTPS  
    hostPort: 443
    protocol: TCP
  - containerPort: 30080   # ArgoCD HTTP
    hostPort: 30080
    protocol: TCP
  - containerPort: 30305   # ArgoCD HTTPS
    hostPort: 30305
    protocol: TCP
EOF
```

### Multi-Node Setup (Optional)

```bash
# For testing load balancing and node failures
cat <<EOF | kind create cluster --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
  - containerPort: 443
    hostPort: 443
  - containerPort: 30080
    hostPort: 30080
  - containerPort: 30305
    hostPort: 30305
- role: worker
- role: worker
EOF
```

## Ingress Controller Setup

### Install NGINX Ingress Controller

```bash
# Install NGINX ingress controller for KinD
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Wait for ingress controller to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s
```

### Verify Ingress Controller

```bash
# Check ingress controller status
kubectl get pods -n ingress-nginx

## Deploy the Application

### Create Namespace
```bash
kubectl create namespace flask-app
```

## ArgoCD Installation for KinD

### Install ArgoCD

```bash
# Create namespace
kubectl create namespace argocd

# Install ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for all components
kubectl wait --for=condition=ready pod --all -n argocd --timeout=300s
```

### Configure External Access

```bash
# Patch ArgoCD service for external access
kubectl patch svc argocd-server -n argocd -p '{"spec":{"type":"NodePort","ports":[{"name":"http","port":80,"targetPort":8080,"nodePort":30080},{"name":"https","port":443,"targetPort":8080,"nodePort":30305}]}}'
```

### Access ArgoCD

```bash
# Get admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d && echo

# Access ArgoCD UI
# HTTP:  http://localhost:30080
# HTTPS: https://localhost:30305
# Username: admin
# Password: (from command above)
```

### Standard Deployment
```bash
kubectl apply -f manifests/Deployment/
```

### Install Argo Rollouts (Required for Canary/BlueGreen)
```bash
kubectl create namespace argo-rollouts
kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml
```

### Canary & Blue/Green Deployments
```bash
kubectl apply -f manifests/Rollout-Canary/

kubectl apply -f manifests/Rollout-BlueGreen/
```

## 🧪 Testing Your Setup

### Test Application Deployment
```bash
# Check all resources
kubectl get all -n flask-app

# Test application endpoints
curl http://localhost/
curl http://localhost/health
curl http://localhost/version
```

### Test CI/CD Pipeline

**1. Make a code change**

**2. Commit and push**

**3. Watch ArgoCD for automatic deployment**

---

**Note**: This setup is optimized for development and learning. For production deployments, consider self-managed or managed Kubernetes services (EKS, GKE, AKS) with proper ingress controllers and load balancers.