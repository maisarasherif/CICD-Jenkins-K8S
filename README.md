# Complete CI/CD Pipeline with Jenkins, Kubernetes & ArgoCD

A comprehensive implementation of modern CI/CD pipeline featuring Jenkins for Continuous Integration and ArgoCD for GitOps-based Continuous Deployment on Kubernetes.

## 🏗️ Architecture Overview

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Developer │    │   Jenkins   │    │ Docker Hub  │    │ Kubernetes  │
│   Commits   │───▶│   CI/CD     │───▶│  Registry   │    │   Cluster   │
│             │    │  Pipeline   │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                           │                                      ▲
                           ▼                                      │
                  ┌─────────────┐                        ┌─────────────┐
                  │ Update Git  │                        │   ArgoCD    │
                  │ Manifests   │───────────────────────▶│   GitOps    │
                  │             │                        │ Controller  │
                  └─────────────┘                        └─────────────┘
```

## 🚀 Features

### CI Pipeline (Jenkins)
- ✅ Automated Docker image building
- ✅ Comprehensive testing with pytest
- ✅ Docker Hub registry integration
- ✅ Automatic manifest updates
- ✅ Git commit automation

### CD Pipeline (ArgoCD)
- ✅ GitOps-based deployment
- ✅ Automatic synchronization
- ✅ Self-healing capabilities
- ✅ Rollback functionality
- ✅ **Standard Deployments** & **Canary Deployments**
- ✅ Web UI for monitoring and management

### Application Features
- ✅ Flask web application with health checks
- ✅ Production-ready with Gunicorn
- ✅ Comprehensive monitoring endpoints
- ✅ Kubernetes-native health probes
- ✅ Resource limits and requests

## 📋 Prerequisites

- **Docker** (v20.10+)
- **Kubernetes cluster** (v1.20+)
- **kubectl** (matching your cluster version)
- **Git** (v2.0+)
- **curl** (for testing)

### For Local Development:
- **KinD** (Kubernetes in Docker) - See [KinD Setup Guide](./docs/kind-setup.md)

## 🏁 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/maisarasherif/CICD-Jenkins-K8S.git
cd CICD-Jenkins-K8S
```

### 2. Choose Deployment Strategy

This project supports two deployment strategies:

#### Option A: Standard Deployment
```bash
# Use standard Kubernetes deployment
kubectl apply -f manifests/standard/
```

#### Option B: Canary Deployment  
```bash
# Use Argo Rollouts for canary deployments
kubectl apply -f manifests/canary/
```

### 3. Set Up Jenkins CI Pipeline

1. **Deploy Jenkins:**
   ```bash
   docker-compose up -d
   ```

2. **Configure Jenkins:**
   - Access Jenkins at `http://localhost:8080`
   - Install required plugins: Docker, Kubernetes CLI, SSH Agent
   - Create pipeline job pointing to this repository
   - Configure Docker Hub credentials
   - Configure GitHub SSH key

3. **Run Pipeline:**
   ```bash
   # Trigger the pipeline manually or push changes to main branch
   ```

### 4. Set Up ArgoCD GitOps

1. **Install ArgoCD:**
   ```bash
   kubectl create namespace argocd
   kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
   ```

2. **Configure ArgoCD Application:**
   - Access ArgoCD UI (see cluster-specific instructions)
   - Connect this Git repository
   - Create application pointing to `manifests/standard/` or `manifests/canary/`
   - Enable auto-sync

## 📁 Project Structure

```
CICD-Jenkins-K8S/
├── README.md                          # This file
├── docker-compose.yaml               # Jenkins setup
├── Dockerfile                        # Jenkins custom image
├── Jenkinsfile                       # CI/CD pipeline definition
├── docs/
│   ├── kind-setup.md                 # KinD cluster setup guide
│   ├── jenkins-setup.md              # Detailed Jenkins configuration
│   └── argocd-setup.md              # ArgoCD installation guide
├── app/                              # Flask application source
│   ├── app.py                        # Main application
│   ├── requirements.txt              # Python dependencies
│   ├── Dockerfile                    # Application container
│   └── tests/
│       └── test_app.py              # Application tests
└── manifests/                        # Kubernetes manifests
    ├── standard/                     # Standard deployment strategy
    │   ├── Deployment.yaml
    │   ├── Service.yaml
    │   └── Ingress.yaml
    └── canary/                       # Canary deployment strategy
        ├── Rollout.yaml
        ├── Service.yaml
        ├── CanaryService.yaml
        └── Ingress.yaml
```

## 🔄 CI/CD Workflow

### Standard Deployment Flow
1. **Developer pushes code** to main branch
2. **Jenkins triggers** and builds Docker image
3. **Tests run** automatically with pytest
4. **Image pushed** to Docker Hub registry
5. **Manifest updated** with new image tag
6. **ArgoCD detects** Git changes
7. **Kubernetes deployment** updates with rolling update

### Canary Deployment Flow
1. **Developer pushes code** to main branch
2. **Jenkins triggers** and builds Docker image
3. **Tests run** automatically with pytest
4. **Image pushed** to Docker Hub registry
5. **Rollout manifest updated** with new image tag
6. **ArgoCD detects** Git changes
7. **Canary rollout begins**:
   - 25% traffic to new version (30s pause)
   - 50% traffic to new version (30s pause)
   - 75% traffic to new version (30s pause)
   - 100% traffic to new version (deployment complete)

## 🔧 Configuration

### Switching Between Deployment Strategies

#### From Standard to Canary:
1. **Update Jenkinsfile** to reference `manifests/Rollout.yaml` instead of `manifests/Deployment.yaml`
2. **Update ArgoCD application** to point to `manifests/canary/` directory
3. **Delete existing deployment**: `kubectl delete deployment flask-app -n flask-app`
4. **Sync ArgoCD** to apply rollout configuration

#### From Canary to Standard:
1. **Update Jenkinsfile** to reference `manifests/Deployment.yaml` instead of `manifests/Rollout.yaml`
2. **Update ArgoCD application** to point to `manifests/standard/` directory
3. **Delete existing rollout**: `kubectl delete rollout flask-app-rollout -n flask-app`
4. **Sync ArgoCD** to apply standard deployment

### Jenkins Pipeline Configuration

The pipeline automatically:
- Builds Docker images with Git SHA tags
- Runs comprehensive tests
- Updates Kubernetes manifests
- Commits changes back to Git

### ArgoCD Configuration

ArgoCD monitors the Git repository and:
- Detects manifest changes within 3 minutes
- Automatically syncs cluster state to Git
- Provides web UI for monitoring deployments
- Supports manual sync and rollback operations

## 📊 Monitoring & Operations

### Health Checks
- **Liveness Probe**: `/health` endpoint
- **Readiness Probe**: `/ready` endpoint
- **Application Metrics**: `/version` endpoint

### ArgoCD Operations
```bash
# Check application status
kubectl get applications -n argocd

# Manual sync
kubectl patch app flask-app -n argocd --type merge -p='{"operation":{"initiatedBy":{"username":"admin"},"sync":{"syncStrategy":{"hook":{},"apply":{"force":false}}}}}'

# Check rollout status (canary deployments)
kubectl argo rollouts get rollout flask-app-rollout -n flask-app

# Manual rollback
kubectl argo rollouts undo rollout flask-app-rollout -n flask-app
```

### Jenkins Operations
```bash
# Access Jenkins
docker-compose logs jenkins

# Restart Jenkins
docker-compose restart jenkins
```

## 🛡️ Security Considerations

### Production Recommendations:
- **ArgoCD**: Change default admin password, enable RBAC
- **Jenkins**: Use proper authentication, secure credential storage
- **Kubernetes**: Use network policies, pod security standards
- **Docker**: Scan images for vulnerabilities, use non-root users
- **Git**: Use signed commits, branch protection rules

### Secret Management:
- Store sensitive data in Kubernetes secrets
- Use sealed-secrets or external secret operators for production
- Never commit credentials to Git

## 🌐 Network & Ingress

> **⚠️ Important**: This project was tested with KinD (Kubernetes in Docker). For other Kubernetes distributions (EKS, GKE, AKS, on-premise), you'll need to configure your own ingress controller and load balancer setup.

For KinD-specific setup including ingress configuration, see: **[KinD Setup Guide](./docs/kind-setup.md)**

## 🧪 Testing

### Application Tests
```bash
# Run tests locally
cd app
pip install -r requirements.txt
python -m pytest tests/ -v
```

### Integration Tests
```bash
# Test the deployed application
curl http://your-cluster-ip/
curl http://your-cluster-ip/health
curl http://your-cluster-ip/version
```

### Deployment Tests
```bash
# Test ArgoCD sync
kubectl patch configmap argocd-cm -n argocd --patch '{"data":{"application.instanceLabelKey":"argocd.argoproj.io/instance"}}'

# Test rollout capabilities (canary deployments)
kubectl argo rollouts promote flask-app-rollout -n flask-app
```

## 🔍 Troubleshooting

### Common Issues:

#### Jenkins Pipeline Fails
```bash
# Check Jenkins logs
docker-compose logs jenkins

# Verify Docker connectivity
docker exec -it jenkins docker ps
```

#### ArgoCD Sync Issues
```bash
# Check ArgoCD application status
kubectl describe application flask-app -n argocd

# Check ArgoCD server logs
kubectl logs deployment/argocd-server -n argocd
```

#### Application Not Accessible
```bash
# Check ingress status
kubectl get ingress -n flask-app

# Check service endpoints
kubectl get endpoints -n flask-app

# Check pod status
kubectl get pods -n flask-app
```

## 📈 Monitoring & Observability

### Recommended Additions:
- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards
- **Jaeger**: Distributed tracing
- **ELK Stack**: Centralized logging

### Application Metrics:
The Flask app exposes several endpoints for monitoring:
- `/health`: Health check
- `/ready`: Readiness check  
- `/version`: Build and version information

## 🚀 Advanced Features

### Canary Deployment Controls
```bash
# Watch rollout progress
kubectl argo rollouts get rollout flask-app-rollout -n flask-app --watch

# Manual promotion to next step
kubectl argo rollouts promote flask-app-rollout -n flask-app

# Abort deployment and rollback
kubectl argo rollouts abort flask-app-rollout -n flask-app
kubectl argo rollouts undo flask-app-rollout -n flask-app
```

### Blue/Green Deployment (Future Enhancement)
- Instant traffic switching
- Full environment duplication
- Zero-downtime deployments
- Resource-intensive but fastest rollback

## 🎯 Next Steps

### Immediate Improvements:
1. **Add automated health checks** to canary deployments
2. **Configure notifications** for deployment events
3. **Set up monitoring** with Prometheus/Grafana
4. **Add integration tests** that run against deployed applications

### Advanced Enhancements:
1. **Multi-environment setup** (dev/staging/production)
2. **Progressive delivery** with feature flags
3. **Chaos engineering** with Chaos Monkey
4. **Security scanning** in CI pipeline

## 📚 Learning Resources

- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [Argo Rollouts Documentation](https://argoproj.github.io/argo-rollouts/)
- [Jenkins Pipeline Documentation](https://www.jenkins.io/doc/book/pipeline/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [GitOps Principles](https://www.gitops.tech/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test thoroughly
4. Update documentation if needed
5. Create a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

**Built with ❤️ for learning modern DevOps practices**

*This project demonstrates enterprise-grade CI/CD practices including GitOps, canary deployments, and infrastructure as code.*