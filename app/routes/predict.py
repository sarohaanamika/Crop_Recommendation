from flask import Blueprint, request, jsonify
import pickle
import numpy as np
import os
from app.utils.validator import CropPredictionInput
from app.utils.logger import setup_logger
from pydantic import ValidationError

predict_bp = Blueprint('predict', __name__)
logger = setup_logger(__name__)

# Load model at startup
MODEL_PATH = os.environ.get('MODEL_PATH', 'app/models/xgboost_model.pkl')

try:
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    logger.info(f"Model loaded successfully from {MODEL_PATH}")
except Exception as e:
    logger.error(f"Error loading model: {str(e)}")
    model = None

# Crop mapping (adjust based on your model's output)
CROP_MAPPING = {
    0: 'Rice', 1: 'Maize', 2: 'Chickpea', 3: 'Kidneybeans',
    4: 'Pigeonpeas', 5: 'Mothbeans', 6: 'Mungbean', 7: 'Blackgram',
    8: 'Lentil', 9: 'Pomegranate', 10: 'Banana', 11: 'Mango',
    12: 'Grapes', 13: 'Watermelon', 14: 'Muskmelon', 15: 'Apple',
    16: 'Orange', 17: 'Papaya', 18: 'Coconut', 19: 'Cotton',
    20: 'Jute', 21: 'Coffee'
}

@predict_bp.route('/predict', methods=['POST'])
def predict():
    """Predict crop recommendation"""
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    try:
        # Validate input
        data = request.get_json()
        validated_data = CropPredictionInput(**data)
        
        # Prepare features
        features = np.array([[
            validated_data.nitrogen,
            validated_data.phosphorus,
            validated_data.potassium,
            validated_data.temperature,
            validated_data.humidity,
            validated_data.ph,
            validated_data.rainfall
        ]])
        
        # Make prediction
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        
        # Get top 3 recommendations
        top_3_indices = np.argsort(probabilities)[-3:][::-1]
        recommendations = [
            {
                'crop': CROP_MAPPING.get(idx, f'Crop_{idx}'),
                'probability': float(probabilities[idx])
            }
            for idx in top_3_indices
        ]
        
        logger.info(f"Prediction made: {CROP_MAPPING.get(prediction, f'Crop_{prediction}')}")
        
        return jsonify({
            'success': True,
            'predicted_crop': CROP_MAPPING.get(prediction, f'Crop_{prediction}'),
            'confidence': float(probabilities[prediction]),
            'top_recommendations': recommendations,
            'input_features': data
        }), 200
        
    except ValidationError as e:
        logger.warning(f"Validation error: {str(e)}")
        return jsonify({'error': 'Invalid input', 'details': e.errors()}), 400
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': 'Prediction failed', 'details': str(e)}), 500

@predict_bp.route('/predict/batch', methods=['POST'])
def predict_batch():
    """Batch prediction endpoint"""
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    try:
        data = request.get_json()
        predictions_list = data.get('predictions', [])
        
        if not predictions_list or len(predictions_list) > 100:
            return jsonify({'error': 'Batch size must be between 1 and 100'}), 400
        
        results = []
        for item in predictions_list:
            validated_data = CropPredictionInput(**item)
            features = np.array([[
                validated_data.nitrogen,
                validated_data.phosphorus,
                validated_data.potassium,
                validated_data.temperature,
                validated_data.humidity,
                validated_data.ph,
                validated_data.rainfall
            ]])
            
            prediction = model.predict(features)[0]
            probability = model.predict_proba(features)[0][prediction]
            
            results.append({
                'predicted_crop': CROP_MAPPING.get(prediction, f'Crop_{prediction}'),
                'confidence': float(probability),
                'input': item
            })
        
        return jsonify({
            'success': True,
            'count': len(results),
            'predictions': results
        }), 200
        
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        return jsonify({'error': 'Batch prediction failed', 'details': str(e)}), 500