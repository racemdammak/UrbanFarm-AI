import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_directory_if_not_exists(directory):
    """Create a directory if it doesn't exist."""
    Path(directory).mkdir(parents=True, exist_ok=True)

def save_json(data, filepath):
    """Save data to a JSON file."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def load_json(filepath):
    """Load data from a JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def create_feature_importance_plot(model, feature_names):
    """Create a feature importance plot for the crop recommendation model."""
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[feature_names[i] for i in indices],
        y=importances[indices]
    ))
    
    fig.update_layout(
        title='Feature Importance for Crop Recommendation',
        xaxis_title='Features',
        yaxis_title='Importance',
        showlegend=False
    )
    
    return fig

def create_prediction_confidence_plot(predictions):
    """Create a confidence plot for model predictions."""
    fig = go.Figure()
    
    for crop, prob in predictions.items():
        fig.add_trace(go.Bar(
            x=[crop],
            y=[prob]
        ))
    
    fig.update_layout(
        title='Prediction Confidence by Crop',
        xaxis_title='Crop',
        yaxis_title='Confidence',
        showlegend=False
    )
    
    return fig

def format_sustainability_tips(tips):
    """Format sustainability tips for display."""
    formatted_tips = []
    for i, tip in enumerate(tips.split('\n'), 1):
        if tip.strip():
            formatted_tips.append(f"{i}. {tip.strip()}")
    return '\n'.join(formatted_tips)

def validate_image_file(file):
    """Validate uploaded image file."""
    allowed_extensions = {'png', 'jpg', 'jpeg'}
    if file.name.split('.')[-1].lower() not in allowed_extensions:
        return False, "Please upload a valid image file (PNG, JPG, or JPEG)"
    return True, None

def validate_soil_parameters(n, p, k, ph):
    """Validate soil parameter inputs."""
    if not (0 <= n <= 140):
        return False, "Nitrogen (N) should be between 0 and 140"
    if not (5 <= p <= 145):
        return False, "Phosphorus (P) should be between 5 and 145"
    if not (5 <= k <= 205):
        return False, "Potassium (K) should be between 5 and 205"
    if not (0 <= ph <= 14):
        return False, "pH should be between 0 and 14"
    return True, None

def create_recommendation_plots(results: Dict[str, Any]) -> plt.Figure:
    """Create plots for crop recommendation results."""
    try:
        # Extract data
        crop = results.get('crop', 'Unknown')
        probabilities = results.get('probabilities', {})
        
        # Sort probabilities
        sorted_crops = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
        crops = [c for c, _ in sorted_crops[:5]]  # Top 5 crops
        probs = [p for _, p in sorted_crops[:5]]  # Top 5 probabilities
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Create bar chart
        bars = ax.bar(
            crops,
            probs,
            color='#2CC985'
        )
        
        # Highlight recommended crop
        for i, c in enumerate(crops):
            if c == crop:
                bars[i].set_color('#0CAB6B')
        
        # Set title and labels
        ax.set_title('Crop Recommendation Results', fontsize=14)
        ax.set_xlabel('Crop', fontsize=12)
        ax.set_ylabel('Confidence Score', fontsize=12)
        
        # Add percentage labels
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.,
                height * 1.01,
                f'{height:.1%}',
                ha='center',
                va='bottom',
                fontsize=10
            )
        
        # Set y-axis to percentage format
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))
        
        # Customize appearance
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_ylim(0, max(probs) * 1.2)
        
        plt.tight_layout()
        return fig
    except Exception as e:
        logger.error(f"Error creating recommendation plots: {str(e)}")
        return plt.Figure()

def format_recommendation_text(results: Dict[str, Any]) -> str:
    """Format crop recommendation results as text."""
    try:
        crop = results.get('crop', 'Unknown')
        confidence = results.get('confidence', 0.0)
        alternatives = results.get('alternatives', [])
        
        text = f"Recommended Crop: {crop}\n"
        text += f"Confidence: {confidence:.1%}\n\n"
        
        if alternatives:
            text += "Alternative Options:\n"
            for i, (alt_crop, alt_conf) in enumerate(alternatives, 1):
                text += f"{i}. {alt_crop} ({alt_conf:.1%})\n"
        
        return text
    except Exception as e:
        logger.error(f"Error formatting recommendation text: {str(e)}")
        return "Error formatting results." 