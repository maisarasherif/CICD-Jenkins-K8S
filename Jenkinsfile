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
        // NEW: SonarQube Analysis Stage
        stage('SonarQube Analysis') {
            steps {
                script {
                    echo "🔍 Running SonarQube code analysis..."
                    
                    // Generate test coverage (optional but recommended)
                    sh '''
                    # Install dependencies for testing and coverage
                    docker run --rm -v $(pwd):/workspace -w /workspace python:3.9-slim sh -c "
                        pip install pytest pytest-cov coverage
                        if [ -f app/requirements.txt ]; then
                            pip install -r app/requirements.txt
                        fi
                        # Run tests with coverage
                        python -m pytest app/tests/ --cov=app --cov-report=xml --cov-report=term-missing --junitxml=test-results.xml || true
                    "
                    '''
                }
                script {
                    echo "🔍 Running SonarQube code analysis..."
                    def scannerHome = tool 'SonarQubeScanner-2'
                    withSonarQubeEnv('SonarQube') {
                        sh """
                        echo "🔍 Starting SonarQube analysis..."
                        
                        # Verify coverage file exists and has content
                        if [ -f coverage.xml ]; then
                            echo "✅ Coverage file found, size: \$(stat -c%s coverage.xml)"
                            echo "Coverage file sample:"
                            head -10 coverage.xml
                        else
                            echo "❌ Coverage file not found!"
                        fi
                        
                        # Run SonarQube scanner with simplified configuration
                        ${scannerHome}/bin/sonar-scanner \
                        -Dsonar.projectKey=flask-cicd-demo \
                        -Dsonar.projectName="Flask CI/CD Demo" \
                        -Dsonar.projectVersion=1.0 \
                        -Dsonar.sources=app \
                        -Dsonar.exclusions=app/tests/**,**/*.pyc,**/__pycache__/** \
                        -Dsonar.tests=app/tests \
                        -Dsonar.test.inclusions=app/tests/**/*.py \
                        -Dsonar.python.coverage.reportPaths=coverage.xml \
                        -Dsonar.python.xunit.reportPath=test-results.xml \
                        -Dsonar.host.url=http://sonarqube:9000 \
                        -Dsonar.login=${SONAR_AUTH_TOKEN}
                        """
                    }
                }
            }
            post {
                always {
                    // Archive test results and coverage reports
                    publishTestResults testResultsPattern: 'test-results.xml'
                    publishCoverage adapters: [coberturaAdapter('coverage.xml')], sourceFileResolver: sourceFiles('STORE_LAST_BUILD')
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
        // NEW: Trivy Security Scan Stage
        //stage('Trivy Security Scan') {
        //    steps {
        //        script {
        //            echo "🛡️ Running Trivy container security scan..."
        //            
        //            // Run Trivy scan and save results
        //            sh """
        //            docker run --rm \
        //                --network cicd-jenkins-k8s_jenkins-network \
        //                -v /var/run/docker.sock:/var/run/docker.sock \
        //                -v \$(pwd):/workspace \
        //                aquasec/trivy image \
        //                --format json \
        //                --output /workspace/trivy-report.json \
        //                $DOCKER_IMAGE:$GIT_SHA
        //            """
        //            
        //            // Display critical and high vulnerabilities
        //            sh """
        //            docker run --rm \
        //                --network cicd-jenkins-k8s_jenkins-network \
        //                -v /var/run/docker.sock:/var/run/docker.sock \
        //                aquasec/trivy image \
        //                --severity HIGH,CRITICAL \
        //                --format table \
        //                $DOCKER_IMAGE:$GIT_SHA
        //            """
        //            
        //            // Fail build if critical vulnerabilities found
                    //sh """
                    //docker run --rm \
                    //    --network cicd-jenkins-k8s_jenkins-network \
                    //    -v /var/run/docker.sock:/var/run/docker.sock \
                    //    aquasec/trivy image \
                    //    --exit-code 1 \
                    //    --severity CRITICAL \
                    //    --quiet \
                    //    $DOCKER_IMAGE:$GIT_SHA
                    //"""
        //        }
        //    }
        //    post {
        //        always {
        //            // Archive security scan results
        //            archiveArtifacts artifacts: 'trivy-report.json', allowEmptyArchive: true
        //        }
        //    }
       // }
        
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
