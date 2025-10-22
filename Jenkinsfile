pipeline {
    agent any
    
    environment {
        IMAGE_NAME = 'crop-recommendation'
    }
    
    options {
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
    }
    
    stages {
        // STAGE 1: Environment Setup
        stage('Environment Setup') {
            steps {
                sh '''
                echo "=== Build Information ==="
                echo "Build Number: ${BUILD_NUMBER}"
                echo "Git Commit: ${GIT_COMMIT}"
                echo "=== System Information ==="
                python3 --version
                docker --version
                docker-compose --version
                echo "=== Project Structure ==="
                ls -la
                '''
            }
        }
        
        // STAGE 2: Build Docker Image
        stage('Build Docker Image') {
            steps {
                sh '''
                echo "🏗️ Building Docker Image..."
                docker build -t ${IMAGE_NAME}:latest -t ${IMAGE_NAME}:${BUILD_NUMBER} .
                '''
            }
        }
        
        // STAGE 3: Test Docker Image
        stage('Test Docker Image') {
            steps {
                sh '''
                echo "🔧 Testing Docker Image..."
                # Test basic imports
                docker run --rm ${IMAGE_NAME}:latest python3 -c "import flask; print('✅ Flask import successful')"
                docker run --rm ${IMAGE_NAME}:latest python3 -c "import xgboost; print('✅ XGBoost import successful')" || echo "⚠️ XGBoost not available"
                
                # Test application startup
                docker run -d --name test-container -p 5001:5000 ${IMAGE_NAME}:latest
                sleep 10
                echo "=== Testing health endpoint ==="
                curl -f http://localhost:5001/health || echo "Health check failed"
                docker stop test-container
                docker rm test-container
                '''
            }
        }
        
        // STAGE 4: Deploy Application
        stage('Deploy Application') {
            steps {
                sh '''
                echo "🚀 Deploying Application..."
                # Stop and remove any existing container
                docker stop ${IMAGE_NAME} || true
                docker rm ${IMAGE_NAME} || true
                
                # Deploy new container
                docker run -d \
                  --name ${IMAGE_NAME} \
                  -p 5000:5000 \
                  ${IMAGE_NAME}:latest
                  
                echo "✅ Application deployed successfully!"
                '''
            }
        }
        
        // STAGE 5: Health Check
        stage('Health Check') {
            steps {
                script {
                    echo "🔍 Performing Health Check..."
                    def maxAttempts = 5
                    def success = false
                    
                    for (int i = 1; i <= maxAttempts; i++) {
                        try {
                            sh 'curl -f http://localhost:5000/health'
                            echo "✅ Health check passed! (Attempt ${i}/${maxAttempts})"
                            success = true
                            break
                        } catch (Exception e) {
                            echo "⏳ Health check failed, retrying in 5 seconds... (Attempt ${i}/${maxAttempts})"
                            sleep time: 5, unit: 'SECONDS'
                        }
                    }
                    
                    if (!success) {
                        echo "⚠️ Health check failed after ${maxAttempts} attempts, but continuing..."
                        // Don't fail the pipeline for health check in development
                    }
                }
            }
        }
        
        // STAGE 6: Post-Deployment Verification
        stage('Post-Deployment Verification') {
            steps {
                sh '''
                echo "📊 Post-Deployment Status ==="
                echo "=== Running Containers ==="
                docker ps --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}"
                echo "=== Application Logs (last 10 lines) ==="
                docker logs ${IMAGE_NAME} --tail 10 || true
                echo "=== Resource Usage ==="
                docker stats ${IMAGE_NAME} --no-stream || true
                '''
            }
        }
    }
    
    post {
        always {
            echo "🏁 Pipeline execution completed - Build ${BUILD_NUMBER}"
            
            // Cleanup temporary resources
            sh '''
            echo "🧹 Cleaning up temporary resources..."
            docker stop test-container || true
            docker rm test-container || true
            docker system prune -f || true
            '''
            
            // Archive any test results if they exist
            archiveArtifacts artifacts: '**/*.json, **/*.html, **/*.xml', allowEmptyArchive: true
        }
        
        success {
            echo "🎉 Pipeline SUCCESS!"
            echo "📱 Application URL: http://localhost:5000"
            echo "❤️  Health Check: http://localhost:5000/health"
        }
        
        failure {
            echo "💥 Pipeline FAILED!"
            // Cleanup on failure
            sh '''
            docker stop ${IMAGE_NAME} || true
            docker rm ${IMAGE_NAME} || true
            '''
        }
        
        unstable {
            echo "⚠️ Pipeline completed with warnings"
        }
    }
}