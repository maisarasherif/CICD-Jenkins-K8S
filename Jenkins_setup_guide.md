# Jenkins CI/CD Setup Guide

Comprehensive guide for setting up Jenkins with Docker-in-Docker for building and deploying containerized applications.

## 🏗️ Architecture

```
┌─────────────────┐
│   Jenkins       │
│   Container     │
│                 │
│ ┌─────────────┐ │    ┌─────────────┐
│ │   Pipeline  │ │    │   DinD      │
│ │   Jobs      │ │───▶│ Container   │
│ │             │ │    │             │
│ └─────────────┘ │    └─────────────┘
└─────────────────┘
```

## 📋 Prerequisites

- Docker (v20.10+)
- Docker Compose (v2.0+)
- Git (v2.0+)
- kubectl (for Kubernetes deployments)

## 🚀 Quick Setup

### 1. Start Jenkins with Docker Compose

```bash
# Clone the repository
git clone https://github.com/maisarasherif/CICD-Jenkins-K8S.git
cd CICD-Jenkins-K8S

# Start Jenkins and DinD
docker-compose up -d

# Check containers are running
docker-compose ps
```

### 2. Initial Jenkins Configuration

```bash
# Get initial admin password
docker-compose logs jenkins | grep -A 5 "Please use the following password"

# Or retrieve from container
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

### 3. Access Jenkins

- **URL**: `http://localhost:8080`
- **Username**: `admin`
- **Password**: (from step 2)

## 🔧 Jenkins Configuration

### Install Required Plugins

1. **Go to**: Manage Jenkins → Manage Plugins → Available
2. **Install these plugins**:
   - Docker Pipeline
   - Kubernetes CLI Plugin
   - SSH Agent Plugin
   - Pipeline: Stage View Plugin
   - Blue Ocean (optional, for better UI)

### Configure Credentials

#### Docker Hub Credentials
1. **Go to**: Manage Jenkins → Manage Credentials → System → Global credentials
2. **Add Credential**:
   - **Kind**: Username with password
   - **ID**: `dockerhub-credentials`
   - **Username**: Your Docker Hub username
   - **Password**: Your Docker Hub password/token

#### GitHub SSH Key (for private repos)
1. **Generate SSH key** (if you don't have one):
   ```bash
   ssh-keygen -t rsa -b 4096 -C "jenkins@yourproject.com"
   ```

2. **Add public key to GitHub**: Settings → SSH and GPG keys → New SSH key

3. **Add private key to Jenkins**:
   - **Kind**: SSH Username with private key
   - **ID**: `github-id`
   - **Username**: `git`
   - **Private Key**: Paste your private key content

### Configure Global Tools

1. **Go to**: Manage Jenkins → Global Tool Configuration
2. **Configure**:
   - **Docker**: Add Docker installation (name: `docker`)
   - **Git**: Usually auto-detected

## 📝 Pipeline Configuration

### Create Pipeline Job

1. **New Item** → **Pipeline** → Enter name: `flask-app-cicd`
2. **Pipeline Definition**: Pipeline script from SCM
3. **SCM**: Git
4. **Repository URL**: Your repository URL
5. **Credentials**: Select your GitHub credentials
6. **Branch**: `*/main`
7. **Script Path**: `Jenkinsfile`

### Pipeline Features

The included Jenkinsfile provides:

#### Stages:
1. **Checkout**: Clone repository
2. **Build**: Create Docker image with Git SHA tag
3. **Test**: Run pytest test suite
4. **Login**: Authenticate with Docker Hub
5. **Push**: Upload image to registry
6. **Update Manifest**: Modify Kubernetes deployment files
7. **Commit**: Push manifest changes back to Git

#### Environment Variables:
```groovy
environment {
    DOCKER_HOST = "tcp://dind:2375"           // Docker-in-Docker connection
    DOCKER_REGISTRY = "docker.io"            // Registry URL
    DOCKER_IMAGE = "maisara99/jenkins-py"    // Your image name
    GIT_SHA = "${env.GIT_COMMIT[0..6]}"      // Short Git commit hash
    BUILD_NUMBER = "latest"                   // Build identifier
    K8S_NAMESPACE = "flask-app"               // Kubernetes namespace
    K8S_DEPLOYMENT_NAME = "flask-app"         // Deployment name
}
```

## 🔄 Pipeline Customization

### For Standard Deployments

Update the "Update Manifest" stage to modify `Deployment.yaml`:

```groovy
stage('Update Manifest') {
    steps {
        sh """
        # Download yq for YAML manipulation
        if [ ! -f ./yq ]; then
            curl -L "https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64" -o yq
            chmod +x yq
        fi
        
        # Update deployment image
        ./yq eval '(.spec.template.spec.containers[] | select(.name == "flask-app") | .image) = "maisara99/jenkins-py:'"${GIT_SHA}"'"' -i manifests/standard/Deployment.yaml
        """
    }
}
```

### For Canary Deployments

Update the "Update Manifest" stage to modify `Rollout.yaml`:

```groovy
stage('Update Manifest') {
    steps {
        sh """
        # Download yq for YAML manipulation
        if [ ! -f ./yq ]; then
            curl -L "https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64" -o yq
            chmod +x yq
        fi
        
        # Update rollout image
        ./yq eval '(.spec.template.spec.containers[] | select(.name == "flask-app") | .image) = "maisara99/jenkins-py:'"${GIT_SHA}"'"' -i manifests/canary/Rollout.yaml
        """
    }
}
```

## 🧪 Testing Pipeline

### Manual Trigger
1. **Go to your pipeline job**
2. **Click "Build Now"**
3. **Monitor the Console Output**

### Automatic Trigger (Webhook)
1. **Go to**: GitHub repository → Settings → Webhooks
2. **Add webhook**:
   - **URL**: `http://your-jenkins-url/github-webhook/`
   - **Content type**: `application/json`
   - **Events**: Just push events

## 📊 Monitoring & Debugging

### Check Pipeline Status
```bash
# View Jenkins logs
docker-compose logs -f jenkins

# Check DinD container
docker-compose logs -f dind

# Verify Docker connectivity from Jenkins
docker exec jenkins docker ps
```

### Common Commands
```bash
# Restart Jenkins
docker-compose restart jenkins

# Access Jenkins container
docker exec -it jenkins bash

# Check Jenkins workspace
docker exec jenkins ls -la /var/jenkins_home/workspace/
```

## 🛠️ Troubleshooting

### Pipeline Fails at Docker Build

**Issue**: Docker daemon not accessible

**Solution**:
```bash
# Check DinD container is running
docker-compose ps dind

# Verify Docker socket
docker exec jenkins env | grep DOCKER_HOST

# Restart containers
docker-compose restart
```

### Git Commit Fails

**Issue**: SSH key not configured or Git credentials missing

**Solution**:
```bash
# Check SSH key in Jenkins
docker exec jenkins ssh -T git@github.com

# Verify credentials are configured in Jenkins UI
# Add SSH key to Jenkins credentials if missing
```

### Image Push Fails

**Issue**: Docker Hub authentication failed

**Solution**:
```bash
# Test Docker Hub login manually
docker exec jenkins docker login

# Verify credentials in Jenkins:
# Manage Jenkins → Manage Credentials → dockerhub-credentials
```

### Manifest Update Fails

**Issue**: yq tool not found or YAML syntax error

**Solution**:
```bash
# Test yq installation manually
docker exec jenkins curl -L "https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64" -o yq
docker exec jenkins chmod +x yq

# Test YAML update
docker exec jenkins ./yq eval '.spec.template.spec.containers[0].image' manifests/standard/Deployment.yaml
```

### Kubernetes Apply Fails

**Issue**: kubectl not configured or cluster not accessible

**Solution**:
```bash
# Copy kubeconfig to Jenkins
docker cp ~/.kube/config jenkins:/var/jenkins_home/.kube/config

# Or configure in pipeline:
sh 'mkdir -p ~/.kube && echo "$KUBECONFIG_CONTENT" > ~/.kube/config'
```

## 🔐 Security Best Practices

### Credentials Management
- **Never hardcode** credentials in Jenkinsfile
- **Use Jenkins credentials store** for all secrets
- **Rotate credentials** regularly
- **Use least privilege** for service accounts

### Docker Security
- **Scan images** for vulnerabilities
- **Use non-root users** in containers
- **Keep base images updated**
- **Limit resource usage**

### Pipeline Security
```groovy
// Example: Secure credential usage
withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
}
```

## 📈 Performance Optimization

### Build Performance
- **Use multi-stage Dockerfiles** to reduce image size
- **Cache dependencies** between builds
- **Parallel pipeline stages** where possible
- **Limit concurrent