import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Data directories
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

# Model paths
CROP_MODEL_PATH = MODELS_DIR / "crop_recommender.joblib"
PLANT_HEALTH_MODEL_PATH = MODELS_DIR / "plant_health.h5"

# Dataset paths
CROP_DATASET_PATH = DATA_DIR / "crop_recommendation.csv"
PLANT_HEALTH_DATASET_PATH = DATA_DIR / "plant_health"

# Model parameters
CROP_FEATURES = [
    'N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'
]

PLANT_HEALTH_CLASSES = [
    'healthy',
    'early_blight',
    'late_blight',
    'leaf_mold',
    'septoria_leaf_spot',
    'spider_mites',
    'target_spot',
    'mosaic_virus',
    'yellow_leaf_curl_virus',
    'bacterial_spot'
]

# Image processing
IMAGE_SIZE = (224, 224)
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Model training parameters
RANDOM_FOREST_PARAMS = {
    'n_estimators': 100,
    'max_depth': 10,
    'random_state': 42
}

CNN_PARAMS = {
    'input_shape': (224, 224, 3),
    'conv_layers': [
        (32, 3),
        (64, 3),
        (64, 3)
    ],
    'dense_layers': [64],
    'output_classes': len(PLANT_HEALTH_CLASSES)
}

# API settings
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"

# Chatbot settings
CHATBOT_MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"  # Replace with accessible model
MAX_RESPONSE_LENGTH = 200
TEMPERATURE = 0.7

# UI settings
APP_TITLE = "UrbanFarm AI"
APP_DESCRIPTION = "AI-powered sustainable urban farming assistant"
APP_ICON = "🌱"

# Validation ranges
SOIL_PARAMETER_RANGES = {
    'N': (0, 140),
    'P': (5, 145),
    'K': (5, 205),
    'ph': (0, 14),
    'temperature': (10, 40),
    'humidity': (20, 100),
    'rainfall': (0, 300)
}

# Treatment recommendations
TREATMENT_RECOMMENDATIONS = {
    'healthy': "Your plant appears healthy! Continue with regular maintenance.",
    'early_blight': "Remove infected leaves and apply fungicide. Improve air circulation.",
    'late_blight': "Remove infected plants immediately. Apply copper-based fungicide.",
    'leaf_mold': "Improve ventilation and reduce humidity. Apply fungicide if needed.",
    'septoria_leaf_spot': "Remove infected leaves. Apply fungicide and improve spacing.",
    'spider_mites': "Spray with insecticidal soap or neem oil. Increase humidity.",
    'target_spot': "Remove infected leaves. Apply fungicide and improve air circulation.",
    'mosaic_virus': "Remove infected plants. Control aphid populations.",
    'yellow_leaf_curl_virus': "Remove infected plants. Control whitefly populations.",
    'bacterial_spot': "Remove infected leaves. Apply copper-based bactericide."
} 