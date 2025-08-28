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
                sed -i "s|^\s*image:\s*maisara99/jenkins-py.*|image: maisara99/jenkins-py:$GIT_SHA|" manifests/Deployment.yaml
                """
            }
        }

        stage('Commit & Push Manifest') {
            steps {
                sh """
                git checkout main
                git config user.email "ci-bot@example.com"
                git config user.name "CI Bot"
                git add manifests/Deployment.yaml
                git commit -m "Update image to $DOCKER_IMAGE:$GIT_SHA"
                git push origin HEAD:main
                """
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