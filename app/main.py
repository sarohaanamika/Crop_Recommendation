from app import create_app
import logging

app = create_app()

# Add health check endpoint
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'message': 'Crop Recommendation API is running'}, 200

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=5000, debug=False)