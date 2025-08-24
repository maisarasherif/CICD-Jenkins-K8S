pipeline {
    agent any

    environment {
        DOCKER_HOST = "tcp://dind:2375"
        DOCKER_REGISTRY = "docker.io"
        DOCKER_IMAGE = "maisara99/jenkins-py"
        BUILD_NUMBER = "latest"
        K8S_NAMESPACE = "flask-app"
        K8S_DEPLOYMENT_NAME = "flask-app"
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Test') {
            steps {
                sh 'docker run --rm $DOCKER_IMAGE:$BUILD_NUMBER python -m pytest tests/ -v'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t $DOCKER_IMAGE:$BUILD_NUMBER -f app/Dockerfile app'
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
                sh 'docker push $DOCKER_IMAGE:$BUILD_NUMBER'
                sh 'docker tag $DOCKER_IMAGE:$BUILD_NUMBER $DOCKER_IMAGE:latest'
                sh 'docker push $DOCKER_IMAGE:latest'
            }
        }

        stage('Deploy to Kubernetes') {
    steps {
        script {
            echo "Deploying to Kubernetes cluster..."
            withCredentials([string(credentialsId: 'k8s-token', variable: 'K8S_TOKEN')]) {
                sh """
                    # Set KUBECONFIG manually using token and server
                    export KUBE_API=https://127.0.0.1:38181
                    export K8S_NAMESPACE=flask-app

                    kubectl config set-cluster jenkins-cluster --server=\$KUBE_API --insecure-skip-tls-verify=true
                    kubectl config set-credentials jenkins-user --token=\$K8S_TOKEN
                    kubectl config set-context jenkins-context --cluster=jenkins-cluster --user=jenkins-user --namespace=\$K8S_NAMESPACE
                    kubectl config use-context jenkins-context

                    # Apply deployment
                    kubectl apply -f manifests/Deployment.yaml --validate=false

                    # Update image
                    kubectl set image deployment/\$K8S_DEPLOYMENT_NAME \$K8S_DEPLOYMENT_NAME=\$DOCKER_IMAGE:\$BUILD_NUMBER -n \$K8S_NAMESPACE

                    # Wait for rollout
                    kubectl rollout status deployment/\$K8S_DEPLOYMENT_NAME -n \$K8S_NAMESPACE --timeout=300s

                    # Verify pods
                    kubectl get pods -n \$K8S_NAMESPACE -l app=\$K8S_DEPLOYMENT_NAME
                """
            }
        }
    }
}

stage('Verify Deployment') {
    steps {
        script {
            echo "Verifying deployment health..."
            withCredentials([string(credentialsId: 'k8s-token', variable: 'K8S_TOKEN')]) {
                sh """
                    export KUBE_API=https://127.0.0.1:38181
                    export K8S_NAMESPACE=flask-app

                    kubectl config set-cluster jenkins-cluster --server=\$KUBE_API --insecure-skip-tls-verify=true
                    kubectl config set-credentials jenkins-user --token=\$K8S_TOKEN
                    kubectl config set-context jenkins-context --cluster=jenkins-cluster --user=jenkins-user --namespace=\$K8S_NAMESPACE
                    kubectl config use-context jenkins-context

                    # Wait for pods
                    kubectl wait --for=condition=ready pod -l app=\$K8S_DEPLOYMENT_NAME -n \$K8S_NAMESPACE --timeout=60s

                    # Get service
                    kubectl get svc -n \$K8S_NAMESPACE

                    # Describe deployment
                    kubectl describe deployment \$K8S_DEPLOYMENT_NAME -n \$K8S_NAMESPACE
                """
            }
        }
    }
}

post {
    always {
        echo 'Pipeline completed'
    }
    success {
        echo 'Deployment successful!'
        script {
            sh 'docker system prune -f'
        }
    }
    failure {
        echo 'Pipeline failed!'
        script {
            withCredentials([string(credentialsId: 'k8s-token', variable: 'K8S_TOKEN')]) {
                sh """
                    export KUBE_API=https://127.0.0.1:38181
                    export K8S_NAMESPACE=flask-app

                    kubectl config set-cluster jenkins-cluster --server=\$KUBE_API --insecure-skip-tls-verify=true
                    kubectl config set-credentials jenkins-user --token=\$K8S_TOKEN
                    kubectl config set-context jenkins-context --cluster=jenkins-cluster --user=jenkins-user --namespace=\$K8S_NAMESPACE
                    kubectl config use-context jenkins-context

                    echo "=== DEBUGGING INFORMATION ==="
                    kubectl get events -n \$K8S_NAMESPACE --sort-by='.lastTimestamp' | tail -10
                    kubectl logs -l app=\$K8S_DEPLOYMENT_NAME -n \$K8S_NAMESPACE --tail=50
                """
            }
        }
    }
}
}
