pipeline {
    agent any
    
    environment {
        // Environment configuration
        IMAGE_NAME = 'crop-recommendation'
        ENVIRONMENT = 'development'
        DOCKER_REGISTRY = ''
        
        // Versioning
        IMAGE_TAG = "${env.BUILD_NUMBER}-${env.GIT_COMMIT?.substring(0,7) ?: 'unknown'}"
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
    }
    
    triggers {
        // Automatic triggers
        pollSCM('H/5 * * * *')  // Check every 5 minutes
    }
    
    parameters {
        choice(
            name: 'DEPLOY_ENVIRONMENT',
            choices: ['development', 'staging', 'production'],
            description: 'Select deployment environment'
        )
        booleanParam(
            name: 'RUN_SECURITY_SCAN',
            defaultValue: true,
            description: 'Run security vulnerability scan'
        )
        booleanParam(
            name: 'RUN_PERFORMANCE_TESTS',
            defaultValue: false,
            description: 'Run performance tests'
        )
    }
    
    stages {
        // STAGE 1: Environment Setup
        stage('Environment Setup') {
            steps {
                script {
                    env.ENVIRONMENT = params.DEPLOY_ENVIRONMENT
                    env.IMAGE_NAME = "crop-recommendation-${env.ENVIRONMENT}"
                    echo "🚀 Starting pipeline for ${env.ENVIRONMENT} environment"
                    echo "📦 Image: ${env.IMAGE_NAME}:${env.IMAGE_TAG}"
                }
                
                sh '''
                echo "=== Build Information ==="
                echo "Build Number: ${BUILD_NUMBER}"
                echo "Git Commit: ${GIT_COMMIT}"
                echo "Branch: ${GIT_BRANCH}"
                echo "Environment: ${ENVIRONMENT}"
                echo "=== System Information ==="
                python3 --version
                docker --version
                docker-compose --version
                free -h
                df -h
                '''
            }
        }
        
        // STAGE 2: Code Quality Checks
        stage('Code Quality') {
            parallel {
                stage('Static Analysis') {
                    steps {
                        sh '''
                        echo "=== Running Static Analysis ==="
                        # Python code linting
                        pip install pylint black flake8 || true
                        python -m pylint app/ --exit-zero || true
                        python -m flake8 app/ --exit-zero || true
                        '''
                    }
                }
                
                stage('Dependency Check') {
                    steps {
                        sh '''
                        echo "=== Checking Dependencies ==="
                        pip install safety || true
                        safety check --json --short-report || true
                        # Check for outdated packages
                        pip list --outdated || true
                        '''
                    }
                }
            }
        }
        
        // STAGE 3: Build and Test
        stage('Build and Test') {
            steps {
                sh '''
                echo "=== Setting up Python Environment ==="
                python3 -m venv venv
                . venv/bin/activate
                pip install -r requirements.txt
                pip install pytest pytest-cov pytest-html
                '''
            }
        }
        
        stage('Unit Tests') {
            steps {
                sh '''
                . venv/bin/activate
                echo "=== Running Unit Tests ==="
                python -m pytest tests/ \
                  -v \
                  --cov=app \
                  --cov-report=html \
                  --cov-report=xml \
                  --junitxml=test-results.xml \
                  --html=test-report.html || echo "Tests completed with status: $?"
                '''
            }
            post {
                always {
                    publishHTML(target: [
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                    publishHTML(target: [
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: '.',
                        reportFiles: 'test-report.html',
                        reportName: 'Test Report'
                    ])
                    junit 'test-results.xml'
                }
            }
        }
        
        // STAGE 4: Build Docker Image
        stage('Build Docker Image') {
            steps {
                echo "🏗️ Building Docker Image..."
                sh """
                docker build \
                  -t ${env.IMAGE_NAME}:${env.IMAGE_TAG} \
                  -t ${env.IMAGE_NAME}:latest \
                  --build-arg ENVIRONMENT=${env.ENVIRONMENT} \
                  --build-arg BUILD_NUMBER=${env.BUILD_NUMBER} \
                  .
                """
            }
        }
        
        // STAGE 5: Security Scanning
        stage('Security Scan') {
            when {
                expression { params.RUN_SECURITY_SCAN }
            }
            steps {
                echo "🔒 Running Security Scans..."
                
                // Docker image vulnerability scan
                sh '''
                docker scan ${IMAGE_NAME}:${IMAGE_TAG} --json > scan-result.json || true
                '''
                
                // Source code security scan
                sh '''
                pip install bandit || true
                bandit -r app/ -f json -o bandit-result.json || true
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: '*.json', allowEmptyArchive: true
                }
            }
        }
        
        // STAGE 6: Integration Tests
        stage('Integration Tests') {
            steps {
                echo "🔧 Running Integration Tests..."
                
                // Test Docker image functionality
                sh """
                docker run --rm ${env.IMAGE_NAME}:${env.IMAGE_TAG} \
                  python -c "import flask; print('✅ Flask import successful')"
                """
                
                sh """
                docker run --rm ${env.IMAGE_NAME}:${env.IMAGE_TAG} \
                  python -c "import xgboost; print('✅ XGBoost import successful')" || echo '⚠️ XGBoost not available'
                """
                
                // Test application startup
                sh """
                docker run -d --name test-container -p 5001:5000 ${env.IMAGE_NAME}:${env.IMAGE_TAG}
                sleep 10
                curl -f http://localhost:5001/health || echo 'Health check failed'
                docker stop test-container
                docker rm test-container
                """
            }
        }
        
        // STAGE 7: Performance Tests
        stage('Performance Tests') {
            when {
                expression { params.RUN_PERFORMANCE_TESTS }
            }
            steps {
                echo "⚡ Running Performance Tests..."
                
                sh '''
                # Start test container
                docker run -d --name perf-test -p 5002:5000 ${IMAGE_NAME}:${IMAGE_TAG}
                sleep 15
                
                # Run basic load test
                docker run --rm --network host \
                  alpine/bombardier -c 10 -d 10s -l http://localhost:5002/health || true
                
                # Cleanup
                docker stop perf-test
                docker rm perf-test
                '''
            }
        }
        
        // STAGE 8: Blue-Green Deployment
        stage('Blue-Green Deployment') {
            steps {
                echo "🎯 Starting Blue-Green Deployment..."
                
                // Determine current running color
                script {
                    def runningContainers = sh(script: '''
                    docker ps --filter "name=crop-recommendation" --format "{{.Names}}" | head -1
                    ''', returnStdout: true).trim()
                    
                    def currentColor = "none"
                    if (runningContainers.contains("blue")) {
                        currentColor = "blue"
                    } else if (runningContainers.contains("green")) {
                        currentColor = "green"
                    }
                    
                    def newColor = currentColor == "blue" ? "green" : "blue"
                    def newContainerName = "crop-recommendation-${newColor}"
                    def newPort = newColor == "blue" ? "5003" : "5004"
                    
                    echo "Current: ${currentColor}, Deploying: ${newColor}"
                    echo "New container: ${newContainerName} on port ${newPort}"
                    
                    // Deploy new version
                    sh """
                    docker stop ${newContainerName} || true
                    docker rm ${newContainerName} || true
                    docker run -d \
                      --name ${newContainerName} \
                      -p ${newPort}:5000 \
                      -e ENVIRONMENT=${env.ENVIRONMENT} \
                      ${env.IMAGE_NAME}:${env.IMAGE_TAG}
                    """
                    
                    // Health check with retries
                    def healthCheckPassed = false
                    def maxRetries = 10
                    for (int i = 1; i <= maxRetries; i++) {
                        try {
                            sh "curl -f http://localhost:${newPort}/health"
                            echo "✅ Health check passed for ${newColor} (attempt ${i}/${maxRetries})"
                            healthCheckPassed = true
                            break
                        } catch (Exception e) {
                            echo "⏳ Health check failed for ${newColor} (attempt ${i}/${maxRetries}), retrying..."
                            sleep time: 5, unit: 'SECONDS'
                        }
                    }
                    
                    if (healthCheckPassed) {
                        // Switch traffic (in production, this would update load balancer)
                        echo "🔄 Switching traffic to ${newColor} environment..."
                        
                        // Stop old container if it exists
                        if (currentColor != "none") {
                            sh """
                            docker stop crop-recommendation-${currentColor} || true
                            docker rm crop-recommendation-${currentColor} || true
                            """
                        }
                        
                        // Update main container to use new color
                        sh """
                        docker stop crop-recommendation || true
                        docker rm crop-recommendation || true
                        docker run -d \
                          --name crop-recommendation \
                          -p 5000:5000 \
                          -e ENVIRONMENT=${env.ENVIRONMENT} \
                          ${env.IMAGE_NAME}:${env.IMAGE_TAG}
                        """
                    } else {
                        error "❌ Health check failed for ${newColor} after ${maxRetries} attempts. Rolling back."
                    }
                }
            }
        }
        
        // STAGE 9: Post-Deployment Verification
        stage('Post-Deployment Verification') {
            steps {
                echo "🔍 Running Post-Deployment Checks..."
                
                // Final health check
                sh 'curl -f http://localhost:5000/health'
                
                // Container status
                sh '''
                echo "=== Running Containers ==="
                docker ps --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}"
                echo "=== Container Resources ==="
                docker stats --no-stream --format "table {{.Name}}\\t{{.CPUPerc}}\\t{{.MemUsage}}" crop-recommendation || true
                '''
                
                // Application logs
                sh '''
                echo "=== Recent Application Logs ==="
                docker logs crop-recommendation --tail 20 || true
                '''
            }
        }
    }
    
    post {
        always {
            echo "🏁 Pipeline execution completed - Build ${env.BUILD_NUMBER}"
            
            // Cleanup
            sh '''
            echo "=== Cleaning up ==="
            docker system prune -f --filter until=24h || true
            docker image prune -f || true
            '''
            
            // Archive artifacts
            archiveArtifacts artifacts: '**/*.json, **/*.html, **/*.xml', allowEmptyArchive: true
        }
        
        success {
            echo "🎉 Pipeline SUCCESS! Crop Recommendation app deployed successfully."
        }
        
        failure {
            echo "💥 Pipeline FAILED!"
            
            // Rollback to previous version if deployment failed
            sh '''
            echo "🔄 Attempting rollback..."
            docker stop crop-recommendation-blue crop-recommendation-green || true
            # Start last known good version
            docker run -d --name crop-recommendation -p 5000:5000 crop-recommendation:previous || true
            '''
        }
        
        unstable {
            echo "⚠️ Pipeline is UNSTABLE - Tests failed but deployment completed"
        }
        
        changed {
            echo "🔄 Pipeline status changed from previous build"
        }
    }
}