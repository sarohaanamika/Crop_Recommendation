from app import create_app
import logging
import os

app = create_app()

# Add version endpoint
@app.route('/health')
def health_check():
    environment = os.getenv('ENVIRONMENT', 'unknown')
    version = os.getenv('VERSION', 'unknown')
    return {
        'status': 'healthy', 
        'message': 'Crop Recommendation API is running',
        'environment': environment,
        'version': version
    }, 200

@app.route('/')
def home():
    environment = os.getenv('ENVIRONMENT', 'unknown')
    version = os.getenv('VERSION', 'unknown')
    return {
        'message': 'Welcome to Crop Recommendation API',
        'environment': environment,
        'version': version
    }, 200

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=5000, debug=False)