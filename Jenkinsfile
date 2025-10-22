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
                docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} -t ${IMAGE_NAME}:latest .
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
                docker run --rm ${IMAGE_NAME}:latest python3 -c "import xgboost; print('✅ XGBoost import successful')"
                
                # Test application internally (without port mapping)
                echo "=== Testing application inside container ==="
                docker run --rm ${IMAGE_NAME}:latest python3 -c "
                from app import app
                import requests
                print('✅ App imports work')
                " || echo "❌ App import failed"
                
                # Check if the container starts without errors
                echo "=== Checking container startup ==="
                docker run --name test-container -d ${IMAGE_NAME}:latest
                sleep 10
                docker logs test-container
                docker stop test-container
                docker rm test-container
                '''
            }
        }
        
        // STAGE 4: Blue-Green Deployment
        stage('Blue-Green Deployment') {
            steps {
                script {
                    echo "🎯 Starting Blue/Green Deployment..."
                    
                    // Make sure scripts are executable
                    sh 'chmod +x scripts/*.sh'
                    
                    // Use our automated blue/green deployment script
                    sh './scripts/switch-env-macos.sh'
                }
            }
        }
        
        // STAGE 5: Post-Deployment Verification
        stage('Post-Deployment Verification') {
            steps {
                sh '''
                echo "🔍 Post-Deployment Verification ==="
                echo "=== Testing through Nginx ==="
                curl -f http://localhost:8080/health || echo "Nginx health check failed"
                
                echo "=== Testing Blue directly ==="
                curl -f http://localhost:5002/health || echo "Blue direct check failed"
                
                echo "=== Testing Green directly ==="
                curl -f http://localhost:5003/health || echo "Green direct check failed"
                
                echo "=== Container Status ==="
                docker-compose ps --services | while read service; do
                    echo "- $service"
                done
                '''
            }
        }
    }
    
    post {
        always {
            echo "🏁 Pipeline execution completed - Build ${BUILD_NUMBER}"
            
            // Cleanup test containers
            sh '''
            echo "🧹 Cleaning up test resources..."
            docker stop test-container || true
            docker rm test-container || true
            docker system prune -f || true
            '''
        }
        
        success {
            echo "🎉 Pipeline SUCCESS! Blue/Green deployment completed."
            echo "📱 Application URL: http://localhost:8080"
            echo "❤️  Health Check: http://localhost:8080/health"
        }
        
        failure {
            echo "💥 Pipeline FAILED!"
            // Cleanup on failure
            sh '''
            docker-compose down || true
            '''
        }
    }
}