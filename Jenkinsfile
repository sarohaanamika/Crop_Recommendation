pipeline {
    agent any
    
    environment {
        IMAGE_NAME = 'crop-recommendation'
        DOCKER_REGISTRY = ''
    }
    
    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', 
                url: 'https://github.com/sarohaanamika/Crop_Recommendation.git'
            }
        }
        
        stage('Install Dependencies') {
            steps {
                sh '''
                python -m venv venv
                . venv/bin/activate
                pip install -r requirements.txt
                pip install pytest pytest-cov
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
                    sleep time: 15, unit: 'SECONDS'
                    def healthResponse = sh(script: 'curl -f http://localhost:5000/health || exit 1', returnStatus: true)
                    if (healthResponse == 0) {
                        echo "✅ Health check passed!"
                    } else {
                        error "❌ Health check failed! Application may not be running."
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo "Pipeline execution completed - Build ${BUILD_NUMBER}"
            sh 'docker system prune -f --filter until=24h'
            junit '**/test-reports/*.xml' 
        }
        success {
            echo "✅ Pipeline succeeded! Crop Recommendation app is deployed and healthy."
        }
        failure {
            echo "❌ Pipeline failed! Check the logs for details."
            sh 'docker-compose down || true'
        }
    }
}
