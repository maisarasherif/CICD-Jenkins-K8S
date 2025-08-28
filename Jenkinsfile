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

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t $DOCKER_IMAGE:$BUILD_NUMBER -f deployment/Dockerfile deployment'
            }
        }
        
        stage('Test') {
            steps {
                sh 'docker run --rm $DOCKER_IMAGE:$BUILD_NUMBER python -m pytest tests/ -v'
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

        //stage('Deploy to Kubernetes') {
            //steps {
            //    withKubeConfig([credentialsId: 'kubeconfig-prod']) {
            //    sh """
            //        # Update image tag in-place (option 1): set image
            //        kubectl -n flask-app set image deployment/flask-app flask-app=${DOCKER_IMAGE}:${BUILD_NUMBER} --record || true

            //        # Wait for rollout
            //        kubectl -n flask-app rollout status deployment/flask-app --timeout=120s
            //    """
            //    }
          //  }
        //}
    }

    //post {
        //failure {
        //withKubeConfig([credentialsId: 'kubeconfig-prod']) {
          //  sh 'kubectl -n flask-app rollout undo deployment/flask-app || true'
        //    }
      //  }
    //}
}