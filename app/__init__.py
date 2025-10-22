from flask import Flask , render_template
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics
from app.config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS
    CORS(app)
    
    # Prometheus metrics
    metrics = PrometheusMetrics(app)
    
    # Register blueprints
    from app.routes.health import health_bp
    from app.routes.predict import predict_bp
    from app.routes.webhook import webhook_bp
    
    app.register_blueprint(health_bp)
    app.register_blueprint(predict_bp)
    app.register_blueprint(webhook_bp)  # Add this line

    # Add root route to serve the HTML page
    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app