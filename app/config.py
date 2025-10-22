import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-prod'
    MODEL_PATH = os.environ.get('MODEL_PATH') or 'app/models/xgboost_model.pkl'
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max request size