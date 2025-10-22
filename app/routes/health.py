from flask import Blueprint, jsonify
import pickle
import os

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'crop-recommendation-api'
    }), 200

@health_bp.route('/readiness', methods=['GET'])
def readiness_check():
    """Readiness check - verify model is loaded"""
    try:
        model_path = os.environ.get('MODEL_PATH', 'app/models/xgboost_model.pkl')
        if os.path.exists(model_path):
            return jsonify({'status': 'ready'}), 200
        else:
            return jsonify({'status': 'not ready', 'reason': 'model not found'}), 503
    except Exception as e:
        return jsonify({'status': 'not ready', 'reason': str(e)}), 503
