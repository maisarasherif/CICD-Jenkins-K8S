# Jenkins CI/CD Setup Guide

Comprehensive guide for setting up Jenkins with Docker-in-Docker for building and deploying containerized applications.

## Architecture

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

## Prerequisites

- Docker 
- Docker Compose 
- Git 
- kubectl (for Kubernetes deployments) (optional)

## Quick Setup

### 1. Start Jenkins with Docker Compose

```bash
# Start Jenkins and DinD
docker-compose up -d
```

### 2. Initial Jenkins Configuration

```bash
# Get initial admin password
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

### 3. Access Jenkins

- **URL**: `http://localhost:8080`
- **Username**: `admin`
- **Password**: (from step 2)

## Jenkins Configuration

### Install Required Plugins

1. **Go to**: Manage Jenkins → Manage Plugins → Available
2. **Install these plugins**:
   - Docker Pipeline
   - Kubernetes CLI Plugin
   - SSH Agent Plugin
   - Pipeline: Stage View Plugin
   - Blue Ocean (optional)

### Configure Credentials

#### Docker Hub Credentials
1. **Go to**: Manage Jenkins → Manage Credentials → System → Global credentials
2. **Add Credential**:
   - **Kind**: Username with password
   - **ID**: `dockerhub-credentials`
   - **Username**: Your Docker Hub username
   - **Password**: Your Docker Hub password/token

#### GitHub SSH Key (for private repos)

1. **Add public key to GitHub**: Settings → SSH and GPG keys → New SSH key

2. **Add private key to Jenkins**:
   - **Kind**: SSH Username with private key
   - **ID**: `github-id`
   - **Username**: `git`
   - **Private Key**: Paste your private key content

### Configure Global Tools

1. **Go to**: Manage Jenkins → Global Tool Configuration
2. **Configure**:
   - **Docker**: Add Docker installation (name: `docker`)
   - **Git**: Usually auto-detected

## Pipeline Configuration

### Create Pipeline Job

1. **New Item** → **Pipeline** → Enter name: `app-cicd`
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
3. **Test**: Run test suite
4. **Login**: Authenticate with Docker Hub
5. **Push**: Upload image to registry
6. **Update Manifest**: Modify Kubernetes deployment files
7. **Commit**: Push manifest changes back to Git

## Testing Pipeline

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