# KinD (Kubernetes in Docker) Setup Guide

This guide provides detailed instructions for setting up this CI/CD project using KinD for local development and testing.

## 🐳 Why KinD?

KinD (Kubernetes in Docker) is perfect for:
- **Local development** and testing
- **CI/CD pipeline** testing
- **Learning Kubernetes** without cloud costs
- **Reproducible environments**

## 📋 Prerequisites

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install kubectl
curl -LO "https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Install KinD
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```

## 🏗️ Cluster Configuration

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

## 🌐 Ingress Controller Setup

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

# Test ingress controller
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: test-ingress
  namespace: default
spec:
  ingressClassName: nginx
  rules:
  - http:
      paths:
      - path: /test
        pathType: Prefix
        backend:
          service:
            name: test-service
            port:
              number: 80
EOF
```

## 🚀 Deploy the Application

### Create Namespace
```bash
kubectl create namespace flask-app
```

### Standard Deployment
```bash
kubectl apply -f manifests/standard/
```

### Canary Deployment (Requires Argo Rollouts)
```bash
# Install Argo Rollouts first
kubectl create namespace argo-rollouts
kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml

# Then deploy canary configuration
kubectl apply -f manifests/canary/
```

## 🔧 ArgoCD Installation for KinD

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
```bash
# Make a code change
echo "# Test change" >> app/app.py

# Commit and push
git add .
git commit -m "Test pipeline"
git push

# Watch ArgoCD for automatic deployment
kubectl get applications -n argocd -w
```

### Test Canary Deployment
```bash
# Watch rollout progress
kubectl argo rollouts get rollout flask-app-rollout -n flask-app --watch

# Manual rollout control
kubectl argo rollouts promote flask-app-rollout -n flask-app
kubectl argo rollouts abort flask-app-rollout -n flask-app
```

## 🔍 Troubleshooting

### Common KinD Issues

#### Port Conflicts
```bash
# Check what's using your ports
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :443

# Kill conflicting processes or use different ports
```

#### Docker Issues
```bash
# Restart Docker daemon
sudo systemctl restart docker

# Clean Docker system
docker system prune -a
```

#### KinD Cluster Issues
```bash
# Check cluster status
kind get clusters
kubectl cluster-info

# Recreate cluster if needed
kind delete cluster
# Run cluster creation command again
```

### Ingress Controller Issues

```bash
# Check ingress controller logs
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller

# Verify ingress class
kubectl get ingressclass
```

### ArgoCD Access Issues

```bash
# Check service configuration
kubectl get svc argocd-server -n argocd

# Port forward as alternative
kubectl port-forward svc/argocd-server -n argocd 8080:80
# Then access: http://localhost:8080
```

## 🗑️ Cleanup

### Remove Everything
```bash
# Delete KinD cluster
kind delete cluster

# Remove Docker containers
docker-compose down -v

# Clean Docker images
docker image prune -a
```

### Partial Cleanup
```bash
# Remove just the application
kubectl delete namespace flask-app

# Remove ArgoCD
kubectl delete namespace argocd

# Remove Argo Rollouts
kubectl delete namespace argo-rollouts
```

## 💡 KinD Best Practices

### Resource Management
- **Limit CPU/Memory** in manifests to prevent resource exhaustion
- **Use multiple nodes** for testing high availability
- **Monitor Docker resources** (`docker stats`)

### Development Workflow
- **Use separate clusters** for different projects
- **Tag clusters** with meaningful names: `kind create cluster --name project-name`
- **Regular cleanup** to free disk space

### Performance Tips
- **Pre-pull images** to speed up deployments
- **Use local registry** for faster image pulls
- **Increase Docker resources** if running multiple clusters

---

**Note**: This setup is optimized for development and learning. For production deployments, consider managed Kubernetes services (EKS, GKE, AKS) with proper ingress controllers and load balancers.