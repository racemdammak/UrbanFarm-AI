import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
from pathlib import Path
import logging

# Configure logging
logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self):
        # Set up paths
        self.data_path = Path(__file__).parent.parent / "data" / "Crop_Recommendation.csv"
        self.model_path = Path(__file__).parent.parent / "models" / "crop_recommender.joblib"
        self.scaler_path = Path(__file__).parent.parent / "models" / "scaler.joblib"
        
        # Initialize components
        self.scaler = None
        self.model = None
        self.feature_names = None
        
        # Expected feature names in the model
        self.expected_features = ['n', 'p', 'k', 'temperature', 'humidity', 'ph', 'rainfall']
        
        # Initialize logger
        self.logger = logging.getLogger(f"{__name__}.DataProcessor")
        
        # Log initialization
        self.logger.info(f"DataProcessor initialized with data path: {self.data_path}")
        self.logger.info(f"Model path set to: {self.model_path}")

    def load_and_clean_data(self):
        """Load and clean the dataset."""
        try:
            # Check if file exists
            if not os.path.exists(self.data_path):
                self.logger.error(f"Data file not found at: {self.data_path}")
                return None
                
            # Load data with error handling
            try:
                df = pd.read_csv(self.data_path)
                self.logger.info(f"Loaded dataset with shape: {df.shape}")
            except pd.errors.EmptyDataError:
                self.logger.error("The CSV file is empty")
                return None
            except pd.errors.ParserError:
                self.logger.error("Error parsing the CSV file - it may be corrupted")
                return None
                
            # Normalize column names
            df = self._normalize_column_names(df)
            
            # Check for missing values
            if df.isnull().sum().any():
                self.logger.info("Found missing values. Handling them...")
                df = df.dropna()
            
            # Check for duplicates
            duplicates = df.duplicated().sum()
            if duplicates > 0:
                self.logger.info(f"Found {duplicates} duplicate rows. Removing them...")
                df = df.drop_duplicates()
            
            # Check for outliers using IQR method
            for column in df.columns:
                if column.lower() not in ['label', 'crop']:  # Skip target column
                    Q1 = df[column].quantile(0.25)
                    Q3 = df[column].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
            
            self.logger.info(f"Cleaned dataset shape: {df.shape}")
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading and cleaning data: {str(e)}", exc_info=True)
            return None
    
    def _normalize_column_names(self, df):
        """Normalize column names to match expected format."""
        # Convert all column names to lowercase
        df.columns = df.columns.str.lower()
        
        # Map common column names to expected format
        column_mapping = {
            'n': 'n',
            'nitrogen': 'n',
            'p': 'p',
            'phosphorus': 'p', 
            'phosphorous': 'p',
            'k': 'k',
            'potassium': 'k',
            'temp': 'temperature',
            'temperature': 'temperature',
            'humidity': 'humidity',
            'ph': 'ph',
            'rainfall': 'rainfall',
            'rain': 'rainfall',
            'precipitation': 'rainfall',
            'label': 'label',
            'crop': 'label'
        }
        
        # Rename columns if they match our mapping
        new_columns = []
        for col in df.columns:
            if col.lower() in column_mapping:
                new_columns.append(column_mapping[col.lower()])
            else:
                new_columns.append(col.lower())
        
        df.columns = new_columns
        
        # Log the column names
        self.logger.info(f"Normalized column names: {list(df.columns)}")
        
        return df
    
    def prepare_data(self, df):
        """Prepare data for training."""
        try:
            # Make sure column names are normalized
            df = self._normalize_column_names(df)
            
            # Identify feature columns (all except 'label')
            feature_columns = [col for col in df.columns if col != 'label']
            target_column = 'label'
            
            # Check if target column exists
            if target_column not in df.columns:
                self.logger.error(f"Required column '{target_column}' not found in dataset")
                return None
                
            # Split features and target
            X = df[feature_columns]
            y = df[target_column]
            
            # Split into train and test sets
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            self.logger.info(f"Training set shape: {X_train.shape}, Test set shape: {X_test.shape}")
            return X_train_scaled, X_test_scaled, y_train, y_test
            
        except Exception as e:
            self.logger.error(f"Error preparing data: {str(e)}", exc_info=True)
            return None
    
    def _train_model(self):
        """Train the crop recommendation model."""
        try:
            # Create model directory if it doesn't exist
            model_dir = os.path.join('app', 'models')
            os.makedirs(model_dir, exist_ok=True)
            
            model_path = os.path.join(model_dir, 'crop_recommender.joblib')
            scaler_path = os.path.join(model_dir, 'scaler.joblib')
            
            # Load and preprocess data
            df = self.load_and_clean_data()
            
            if df is None or df.empty:
                self.logger.error("Failed to load or clean data")
                return False
                
            self.logger.info(f"Data loaded successfully with shape: {df.shape}")
            
            # Separate features and target
            if 'label' not in df.columns:
                self.logger.error("Required column 'label' not found in dataset")
                return False
                
            # Identify feature columns (all except 'label')
            feature_columns = [col for col in df.columns if col != 'label']
            self.logger.info(f"Using feature columns: {feature_columns}")
            
            X = df[feature_columns]
            y = df['label']
            
            # Scale the features
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            
            # Train-test split
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )
            
            # Train the model
            self.logger.info("Training Random Forest model...")
            self.model = RandomForestClassifier(
                n_estimators=100, 
                random_state=42
            )
            self.model.fit(X_train, y_train)
            
            # Evaluate the model
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            self.logger.info(f"Model trained with accuracy: {accuracy:.4f}")
            
            # Save model and scaler
            self.logger.info(f"Saving model to: {model_path}")
            joblib.dump(self.model, model_path)
            
            self.logger.info(f"Saving scaler to: {scaler_path}")
            joblib.dump(self.scaler, scaler_path)
            
            self.logger.info("Model and scaler saved successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error training model: {str(e)}", exc_info=True)
            return False
    
    def load_model(self):
        """Load the trained model and scaler."""
        try:
            if not self.model_path.exists() or not self.scaler_path.exists():
                self.logger.warning("Model or scaler file not found. Training new model...")
                return self.train_model()
            
            # Load model and scaler
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
            
            self.logger.info("Model and scaler loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}", exc_info=True)
            return False
    
    def predict(self, features):
        """Make a prediction using the trained model."""
        try:
            # Check if model is loaded
            if self.model is None:
                self.logger.warning("Model not loaded. Attempting to load model...")
                if not self.load_model():
                    self.logger.warning("Model loading failed. Attempting to train new model...")
                    if not self.train_model():
                        raise Exception("Failed to load or train model")

            # Check if scaler is loaded
            if self.scaler is None:
                self.logger.error("Scaler not loaded")
                return None

            # Convert input features to expected format
            input_features = self._normalize_input_features(features)
            if input_features is None:
                raise ValueError("Could not normalize input features")

            # Scale features
            scaled_features = self.scaler.transform([input_features])
            
            # Make prediction
            prediction = self.model.predict(scaled_features)
            probabilities = self.model.predict_proba(scaled_features)
            
            # Get top 3 predictions with probabilities
            top_3_idx = probabilities[0].argsort()[-3:][::-1]
            top_3_crops = [
                (self.model.classes_[idx], probabilities[0][idx])
                for idx in top_3_idx
            ]
            
            self.logger.info(f"Prediction successful. Top prediction: {top_3_crops[0][0]}")
            return {
                'prediction': prediction[0],
                'top_3': top_3_crops,
                'confidence': float(probabilities[0].max())
            }
            
        except Exception as e:
            self.logger.error(f"Error making prediction: {str(e)}", exc_info=True)
            return None

    def _normalize_input_features(self, features):
        """Normalize input features to match expected model input format."""
        try:
            # Define mappings for input feature names
            feature_mappings = {
                'nitrogen': 'n',
                'n': 'n',
                'phosphorus': 'p',
                'p': 'p',
                'potassium': 'k',
                'k': 'k',
                'temperature': 'temperature',
                'temp': 'temperature',
                'humidity': 'humidity',
                'ph': 'ph',
                'ph_value': 'ph',
                'rainfall': 'rainfall',
                'rain': 'rainfall'
            }
            
            # Initialize normalized features dictionary
            normalized = {}
            
            # Convert input features to normalized format
            for key, value in features.items():
                key_lower = key.lower()
                if key_lower in feature_mappings:
                    normalized[feature_mappings[key_lower]] = float(value)
                    
            # Check if all required features are present
            missing_features = set(self.expected_features) - set(normalized.keys())
            if missing_features:
                self.logger.error(f"Missing required features: {missing_features}")
                return None
                
            # Return features in correct order
            return [normalized[feature] for feature in self.expected_features]
            
        except Exception as e:
            self.logger.error(f"Error normalizing input features: {str(e)}", exc_info=True)
            return None

    def get_feature_importance(self):
        """Get feature importance scores."""
        try:
            if self.model is None:
                if not self.load_model():
                    return None
            
            importances = self.model.feature_importances_
            return dict(zip(self.expected_features, importances))
            
        except Exception as e:
            self.logger.error(f"Error getting feature importance: {str(e)}")
            return None
    
    def train_model(self):
        """Train a new model."""
        try:
            # Create model directory if it doesn't exist
            os.makedirs(self.model_path.parent, exist_ok=True)
            
            # Load and preprocess data
            df = self.load_and_clean_data()
            if df is None or df.empty:
                raise ValueError("Failed to load or clean data")
            
            # Initialize scaler
            self.scaler = StandardScaler()
            
            # Prepare features and target
            X = df[self.expected_features]
            y = df['label']
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )
            
            # Train model with optimized parameters
            self.model = RandomForestClassifier(
                n_estimators=200,
                max_depth=20,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1  # Use all available cores
            )
            
            # Fit model
            self.model.fit(X_train, y_train)
            
            # Evaluate model
            train_accuracy = self.model.score(X_train, y_train)
            test_accuracy = self.model.score(X_test, y_test)
            
            self.logger.info(f"Model trained successfully:")
            self.logger.info(f"Training accuracy: {train_accuracy:.4f}")
            self.logger.info(f"Testing accuracy: {test_accuracy:.4f}")
            
            # Save model and scaler
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error training model: {str(e)}", exc_info=True)
            return False 