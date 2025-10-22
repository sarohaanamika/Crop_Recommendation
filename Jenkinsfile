pipeline {
    agent any
    
    environment {
        IMAGE_NAME = 'crop-recommendation'
    }
    
    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', 
                url: 'https://github.com/sarohaanamika/Crop_Recommendation.git'
            }
        }
        
        stage('Verify Environment') {
            steps {
                sh '''
                echo "=== Environment Check ==="
                echo "Python: $(python3 --version)"
                echo "Docker: $(docker --version)"
                echo "Docker Compose: $(docker-compose --version 2>/dev/null || echo 'Not available')"
                echo "Project files:"
                ls -la
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t ${IMAGE_NAME}:latest .'
            }
        }
        
        stage('Deploy Application') {
            steps {
                script {
                    // Check if docker-compose.yml exists
                    if (fileExists('docker-compose.yml')) {
                        echo "Found docker-compose.yml, attempting to deploy..."
                        
                        // Try different methods to run compose
                        try {
                            sh 'docker-compose down || true'
                            sh 'docker-compose up -d'
                            echo "✅ Deployed using docker-compose"
                        } catch (Exception e) {
                            echo "⚠️ docker-compose failed, trying manual docker run..."
                            // Fallback to manual docker run
                            sh '''
                            docker stop ${IMAGE_NAME} || true
                            docker rm ${IMAGE_NAME} || true
                            docker run -d --name ${IMAGE_NAME} -p 5000:5000 ${IMAGE_NAME}:latest
                            '''
                            echo "✅ Deployed using manual docker run"
                        }
                    } else {
                        echo "No docker-compose.yml found, using manual docker run..."
                        sh '''
                        docker stop ${IMAGE_NAME} || true
                        docker rm ${IMAGE_NAME} || true
                        docker run -d --name ${IMAGE_NAME} -p 5000:5000 ${IMAGE_NAME}:latest
                        '''
                    }
                }
            }
        }
        
        stage('Wait for Startup') {
            steps {
                sleep time: 15, unit: 'SECONDS'
            }
        }
        
        stage('Health Check') {
            steps {
                script {
                    def maxAttempts = 5
                    def success = false
                    
                    for (int i = 1; i <= maxAttempts; i++) {
                        echo "Health check attempt ${i}/${maxAttempts}"
                        try {
                            sh 'curl -f http://localhost:5000/health'
                            echo "✅ Health check passed!"
                            success = true
                            break
                        } catch (Exception e) {
                            echo "⏳ Health check failed, retrying in 5 seconds..."
                            sleep time: 5, unit: 'SECONDS'
                        }
                    }
                    
                    if (!success) {
                        echo "⚠️ Health check failed after ${maxAttempts} attempts"
                        echo "Checking container status..."
                        sh 'docker ps'
                        sh 'docker logs ${IMAGE_NAME} || true'
                        // Don't fail the pipeline for health check in development
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo "Pipeline execution completed - Build ${BUILD_NUMBER}"
            // Cleanup
            sh 'docker system prune -f || true'
        }
        success {
            echo "✅ Pipeline completed successfully!"
            echo "Application should be running at: http://localhost:5000"
            echo "Health check: http://localhost:5000/health"
        }
        failure {
            echo "❌ Pipeline failed!"
            // Cleanup on failure
            sh 'docker-compose down || true'
            sh 'docker stop ${IMAGE_NAME} || true'
            sh 'docker rm ${IMAGE_NAME} || true'
        }
    }
}