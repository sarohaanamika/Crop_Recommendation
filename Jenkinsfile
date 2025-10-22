pipeline {
    agent any
    
    environment {
        IMAGE_NAME = 'crop-recommendation'
        DOCKER_REGISTRY = ''  // Add if using ECR/Docker Hub later
    }
    
    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', 
                url: 'https://github.com/sarohaanamika/Crop_Recommendation.git',
                credentialsId: 'github-token'
            }
        }
        
        stage('Install Dependencies') {
            steps {
                sh '''
                python -m venv venv
                . venv/bin/activate
                pip install -r requirements.txt
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                . venv/bin/activate
                python -m pytest tests/ -v --cov=app --cov-report=html
                '''
            }
            post {
                always {
                    // Publish test results
                    publishHTML(target: [
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Test Coverage Report'
                    ])
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t ${IMAGE_NAME}:latest -t ${IMAGE_NAME}:${BUILD_NUMBER} .'
            }
        }
        
        stage('Test Docker Image') {
            steps {
                sh '''
                docker run --rm ${IMAGE_NAME}:latest python -c "import flask; print('Flask imported successfully')"
                docker run --rm ${IMAGE_NAME}:latest python -c "import xgboost; print('XGBoost imported successfully')"
                '''
            }
        }
        
        stage('Security Scan') {
            steps {
                sh '''
                # Basic security check - install trivy or other scanner if needed
                docker scan ${IMAGE_NAME}:latest || echo "Docker scan not available, continuing..."
                '''
            }
        }
        
        stage('Deploy to Local Environment') {
            steps {
                sh '''
                docker-compose down || true
                docker-compose up -d
                '''
            }
        }
        
        stage('Health Check') {
            steps {
                script {
                    // Wait for app to start
                    sleep time: 15, unit: 'SECONDS'
                    
                    // Test if application is responding - try multiple endpoints
                    def healthResponse = sh(script: 'curl -f http://localhost:5000/health || exit 1', returnStatus: true)
                    if (healthResponse == 0) {
                        echo "✅ Health check passed!"
                    } else {
                        // Try the main endpoint if health doesn't exist yet
                        def mainResponse = sh(script: 'curl -f http://localhost:5000/ || curl -f http://localhost:5000/api/ || exit 1', returnStatus: true)
                        if (mainResponse != 0) {
                            error "Application health check failed! Neither /health nor main endpoint responded."
                        } else {
                            echo "✅ Main endpoint is responding (health endpoint not implemented)"
                        }
                    }
                }
            }
        }
    
    post {
        always {
            echo "Pipeline execution completed - Build ${BUILD_NUMBER}"
            // Cleanup
            sh 'docker system prune -f --filter until=24h'
            
            // Archive test results
            junit '**/test-reports/*.xml' 
        }
        success {
            echo "✅ Pipeline succeeded! Crop Recommendation app is deployed and healthy."
            // You can add notifications here (Slack, Email, etc.)
        }
        failure {
            echo "❌ Pipeline failed! Check the logs for details."
            // Rollback if needed
            sh 'docker-compose down || true'
        }
        unstable {
            echo "⚠️ Pipeline is unstable - tests failed but deployment continued"
        }
    }
}