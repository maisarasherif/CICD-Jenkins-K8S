pipeline {
    agent any

    triggers {
        githubPush()
    }

    environment {
        DOCKER_HOST = "tcp://dind:2375"
        DOCKER_REGISTRY = "docker.io"
        DOCKER_IMAGE = "maisara99/jenkins-py"
        GIT_SHA = "${env.GIT_COMMIT[0..6]}"
        //TRIVY_VERSION = "0.45.0"
        TRIVY_IMAGE = "aquasec/trivy:0.45.0"
        BUILD_NUMBER = "latest"
        K8S_NAMESPACE = "flask-app"
        K8S_DEPLOYMENT_NAME = "flask-app"
        DEPLOYMENT_STRATEGY = "BlueGreen"  //1. Standard    2. Canary   3. BlueGreen
    }

    stages {

        stage('SCM Skip Check') {
            steps {
                scmSkip(deleteBuild: true, skipPattern:'.*\\[skip ci\\].*')
            }
        }

        stage('Checkout') {
            steps { 
                checkout scm 
            }
        }
        
        stage('SonarQube Analysis') {
            steps {
                script {
                    echo "🔍 Running SonarQube code analysis..."
                    def scannerHome = tool 'SonarQubeScanner-2'
                    withSonarQubeEnv('SonarQube') {
                        sh "${scannerHome}/bin/sonar-scanner"
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image..."
                    def buildDate = new Date().format("yyyy-MM-dd'T'HH:mm:ss'Z'")
                    sh """
                    docker build -t $DOCKER_IMAGE:$GIT_SHA \
                        --build-arg BUILD_DATE="${buildDate}" \
                        --build-arg VCS_REF=${env.GIT_COMMIT} \
                        --build-arg VERSION=2.0.0 \
                        -f app/Dockerfile app
                    """
                }
            }
        }

        stage('Pull Trivy') {
            steps {
                script {
                    sh "docker pull ${TRIVY_IMAGE}"
                }
            }
        }
        
        stage('Trivy Filesystem Scan') {
            steps {
                script {
                    sh '''
                        # Scan filesystem for vulnerabilities using Docker
                        docker run --rm \
                            -v ${WORKSPACE}:/workspace \
                            -v /tmp/.trivy-cache:/root/.cache/trivy \
                            ${TRIVY_IMAGE} fs /workspace \
                            --format json \
                            --output /workspace/trivy-fs-report.json
                        
                        # Also generate human-readable report
                        docker run --rm \
                            -v ${WORKSPACE}:/workspace \
                            -v /tmp/.trivy-cache:/root/.cache/trivy \
                            ${TRIVY_IMAGE} fs /workspace \
                            --format table \
                            --output /workspace/trivy-fs-report.txt
                    '''
                }
            }
        }
        
        stage('Trivy Container Image Scan') {
            steps {
                script {
                    sh '''
                        # Scan the built Docker image
                        docker run --rm \
                            -v /var/run/docker.sock:/var/run/docker.sock \
                            -v ${WORKSPACE}:/workspace \
                            -v /tmp/.trivy-cache:/root/.cache/trivy \
                            ${TRIVY_IMAGE} image $DOCKER_IMAGE:$GIT_SHA \
                            --format json \
                            --output /workspace/trivy-image-report.json
                        
                        # Generate table format for easy reading
                        docker run --rm \
                            -v /var/run/docker.sock:/var/run/docker.sock \
                            -v ${WORKSPACE}:/workspace \
                            -v /tmp/.trivy-cache:/root/.cache/trivy \
                            ${TRIVY_IMAGE} image $DOCKER_IMAGE:$GIT_SHA \
                            --format table \
                            --output /workspace/trivy-image-report.txt
                        
                        # Show critical and high severity issues
                        echo "=== CRITICAL AND HIGH SEVERITY VULNERABILITIES ==="
                        docker run --rm \
                            -v /var/run/docker.sock:/var/run/docker.sock \
                            -v /tmp/.trivy-cache:/root/.cache/trivy \
                            ${TRIVY_IMAGE} image $DOCKER_IMAGE:$GIT_SHA \
                            --severity HIGH,CRITICAL \
                            --format table
                    '''
                }
            }
        }
        
        stage('Test') {
            steps {
                script {

                    echo "Running application tests..."
                    sh 'docker run --rm $DOCKER_IMAGE:$GIT_SHA python -m pytest tests/ -v'
                }
            }
        }

        stage('Login to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                }
            }
        }

        stage('Push Image') {
            steps {
                script {

                    echo "📤 Pushing image to registry (Docker Hub)..."
                    sh 'docker push $DOCKER_IMAGE:$GIT_SHA'
                }  
            }
        }

        stage('Update Manifest') {
            steps {
                script {
                    if (env.DEPLOYMENT_STRATEGY == 'BlueGreen') {
                        echo "Updating Blue/Green manifest..."
                        updateBlueGreenManifest()
                    } else if (env.DEPLOYMENT_STRATEGY == 'Canary') {
                        echo "Updating Canary manifest..."
                        updateCanaryManifest()
                    } else {
                        echo "Updating Standard manifest..."
                        updateStandardManifest()
                    }
                }
            }
        }

        stage('Commit & Push Manifest') {
            steps {
                sshagent(['github-id']) {
                    script {
                        echo "Committing manifest changes..."
                        sh '''
                        mkdir -p ~/.ssh
                        ssh-keyscan github.com >> ~/.ssh/known_hosts
                        git config user.email "ci-bot@example.com"
                        git config user.name "CI Bot"
                    
                        if [ "$DEPLOYMENT_STRATEGY" = "BlueGreen" ]; then
                            git add manifests/Rollout-BlueGreen/

                        elif [ "$DEPLOYMENT_STRATEGY" = "Canary" ]; then
                            git add manifests/Rollout-Canary/

                        else 
                            git add manifests/Deployment/
                        fi

                        if git diff --staged --quiet; then
                            echo "No changes to commit"
                            exit 0
                        fi

                        git commit -m "Update ${DEPLOYMENT_STRATEGY} deployment image to ${GIT_SHA} [skip ci]" || true

                        git fetch origin main
                        git rebase origin/main || {
                            echo "Rebase failed, trying merge strategy"
                            git rebase --abort
                            git merge origin/main
                        }

                        git push git@github.com:maisarasherif/CICD-Jenkins-K8S.git HEAD:main
                        '''
                    }
                    
                }
            }
        }
    }
}
def updateBlueGreenManifest() {
    sh """
    echo "Current image in Blue/Green rollout:"
    grep -n "image:" manifests/Rollout-BlueGreen/Rollout.yaml || echo "No image line found"
    
    # Download yq yaml editor
    if [ ! -f ./yq ]; then
        curl -L "https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64" -o yq
        chmod +x yq
    fi
    
    # Update the Blue/Green rollout image
    ./yq eval '(.spec.template.spec.containers[] | select(.name == "flask-app") | .image) = "maisara99/jenkins-py:'"${GIT_SHA}"'"' -i manifests/Rollout-BlueGreen/Rollout.yaml
    
    echo "Updated image in Blue/Green rollout:"
    grep -n "image:" manifests/Rollout-BlueGreen/Rollout.yaml
    """
}
def updateCanaryManifest() {
    sh """
    echo "Current image in Canary rollout:"
    grep -n "image:" manifests/Rollout-Canary/Rollout.yaml || echo "No image line found"
    
    # Download yq yaml editor
    if [ ! -f ./yq ]; then
        curl -L "https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64" -o yq
        chmod +x yq
    fi
    
    # Update the Canary rollout image
    ./yq eval '(.spec.template.spec.containers[] | select(.name == "flask-app") | .image) = "maisara99/jenkins-py:'"${GIT_SHA}"'"' -i manifests/Rollout-Canary/Rollout.yaml
    
    echo "Updated image in Canary rollout:"
    grep -n "image:" manifests/Rollout-Canary/Rollout.yaml
    """
}
def updateStandardManifest() {
    sh """
    echo "Current image in Standard deployment:"
    grep -n "image:" manifests/Deployment/Deployment.yaml || echo "No image line found"
    
    # Download yq yaml editor
    if [ ! -f ./yq ]; then
        curl -L "https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64" -o yq
        chmod +x yq
    fi
    
    # Update the Standard deployment image
    ./yq eval '(.spec.template.spec.containers[] | select(.name == "flask-app") | .image) = "maisara99/jenkins-py:'"${GIT_SHA}"'"' -i manifests/Deployment/Deployment.yaml
    
    echo "Updated image in Standard deployment:"
    grep -n "image:" manifests/Deployment/Deployment.yaml
    """
}
