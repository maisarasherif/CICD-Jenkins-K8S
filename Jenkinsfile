pipeline {
    agent any

    environment {
        DOCKER_HOST = "tcp://dind:2375"
        DOCKER_REGISTRY = "docker.io"
        DOCKER_IMAGE = "maisara99/jenkins-py"
        GIT_SHA = "${env.GIT_COMMIT[0..6]}"
        BUILD_NUMBER = "latest"
        K8S_NAMESPACE = "flask-app"
        K8S_DEPLOYMENT_NAME = "flask-app"
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t $DOCKER_IMAGE:$GIT_SHA -f app/Dockerfile app'
            }
        }
        
        stage('Test') {
            steps {
                sh 'docker run --rm $DOCKER_IMAGE:$GIT_SHA python -m pytest tests/ -v'
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
                //sh 'docker push $DOCKER_IMAGE:$BUILD_NUMBER'
                //sh 'docker tag $DOCKER_IMAGE:$BUILD_NUMBER $DOCKER_IMAGE:$GIT_SHA'
                sh 'docker push $DOCKER_IMAGE:$GIT_SHA'
            }
        }

        stage('Update Manifest') {
            steps {
                sh """
                echo "Current image line:"
                grep -n "image:" manifests/Deployment/Deployment.yaml || echo "No image line found"
                
                # Download yq if needed
                if [ ! -f ./yq ]; then
                    curl -L "https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64" -o yq
                    chmod +x yq
                fi
                
                # Use yq to update (most reliable)
                ./yq eval '(.spec.template.spec.containers[] | select(.name == "flask-app") | .image) = "maisara99/jenkins-py:'"${GIT_SHA}"'"' -i manifests/Deployment/Deployment.yaml
                
                echo "Updated image line:"
                grep -n "image:" manifests/Deployment/Deployment.yaml
                """
            }
        }

        stage('Commit & Push Manifest') {
            steps {
                sshagent(['github-id']) {
                    sh '''
                    mkdir -p ~/.ssh
                    ssh-keyscan github.com >> ~/.ssh/known_hosts
                    git config user.email "ci-bot@example.com"
                    git config user.name "CI Bot"
                    git add manifests/Deployment/Deployment.yaml
                    git commit -m "Update image" || true
                    git push git@github.com:maisarasherif/CICD-Jenkins-K8S.git HEAD:main
                    '''
                }
            }
        }
    }
}