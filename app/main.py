from app import create_app
import logging

app = create_app()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=5000, debug=False)