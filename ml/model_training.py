#!/usr/bin/env python3
"""
ML Model Training Pipeline for AI-RecoverOps
"""

import pandas as pd
import numpy as np
import json
import pickle
import mlflow
import mlflow.sklearn
import mlflow.xgboost
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import xgboost as xgb
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Embedding, Dropout
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')

class LogAnalysisMLPipeline:
    def __init__(self, data_path: str = 'data/training_logs.csv'):
        self.data_path = data_path
        self.df = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        
        # Model components
        self.tfidf_vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
        self.label_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        self.tokenizer = Tokenizer(num_words=5000)
        
        # Models
        self.xgb_model = None
        self.lstm_model = None
        self.ensemble_model = None
        
        # MLflow setup
        mlflow.set_experiment("ai-recoverops-training")
        
    def load_and_preprocess_data(self):
        """Load and preprocess the training data"""
        print("Loading and preprocessing data...")
        
        # Load data
        self.df = pd.read_csv(self.data_path)
        
        # Parse metadata JSON
        self.df['metadata'] = self.df['metadata'].apply(
            lambda x: json.loads(x) if isinstance(x, str) else {}
        )
        
        # Extract features from metadata
        self.df['cpu_usage'] = self.df['metadata'].apply(
            lambda x: x.get('cpu_usage', 0) if x else 0
        )
        self.df['memory_usage'] = self.df['metadata'].apply(
            lambda x: x.get('memory_usage', 0) if x else 0
        )
        self.df['disk_usage'] = self.df['metadata'].apply(
            lambda x: x.get('disk_usage', 0) if x else 0
        )
        self.df['response_time'] = self.df['metadata'].apply(
            lambda x: x.get('response_time', 0) if x else 0
        )
        
        # Convert timestamp to datetime features
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        self.df['hour'] = self.df['timestamp'].dt.hour
        self.df['day_of_week'] = self.df['timestamp'].dt.dayofweek
        self.df['is_weekend'] = (self.df['day_of_week'] >= 5).astype(int)
        
        # Encode categorical variables
        categorical_features = ['log_level', 'service', 'aws_service', 'region', 'environment']
        for feature in categorical_features:
            le = LabelEncoder()
            self.df[f'{feature}_encoded'] = le.fit_transform(self.df[feature].fillna('unknown'))
        
        # Create severity score
        severity_map = {'info': 1, 'medium': 2, 'high': 3, 'critical': 4}
        self.df['severity_score'] = self.df['severity'].map(severity_map).fillna(1)
        
        print(f"Loaded {len(self.df)} samples")
        print(f"Incident type distribution:")
        print(self.df['incident_type'].value_counts())
        
    def feature_engineering(self):
        """Extract and engineer features for ML models"""
        print("Engineering features...")
        
        # Text features using TF-IDF
        text_features = self.tfidf_vectorizer.fit_transform(self.df['message'].fillna(''))
        
        # Numerical features
        numerical_features = [
            'cpu_usage', 'memory_usage', 'disk_usage', 'response_time',
            'hour', 'day_of_week', 'is_weekend', 'severity_score',
            'log_level_encoded', 'service_encoded', 'aws_service_encoded',
            'region_encoded', 'environment_encoded'
        ]
        
        numerical_data = self.df[numerical_features].fillna(0)
        numerical_data_scaled = self.scaler.fit_transform(numerical_data)
        
        # Combine features
        from scipy.sparse import hstack
        X = hstack([text_features, numerical_data_scaled])
        
        # Target variable
        y = self.label_encoder.fit_transform(self.df['incident_type'])
        
        # Split data
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"Training set: {self.X_train.shape}")
        print(f"Test set: {self.X_test.shape}")
        
    def train_xgboost_model(self):
        """Train XGBoost classifier"""
        print("Training XGBoost model...")
        
        with mlflow.start_run(run_name="xgboost_training"):
            # Hyperparameter tuning
            param_grid = {
                'n_estimators': [100, 200],
                'max_depth': [6, 8, 10],
                'learning_rate': [0.1, 0.2],
                'subsample': [0.8, 0.9]
            }
            
            xgb_classifier = xgb.XGBClassifier(
                objective='multi:softprob',
                random_state=42,
                n_jobs=-1
            )
            
            # Grid search with cross-validation
            grid_search = GridSearchCV(
                xgb_classifier, param_grid, cv=3, scoring='accuracy', n_jobs=-1
            )
            
            grid_search.fit(self.X_train, self.y_train)
            self.xgb_model = grid_search.best_estimator_
            
            # Predictions
            y_pred = self.xgb_model.predict(self.X_test)
            accuracy = accuracy_score(self.y_test, y_pred)
            
            # Log metrics
            mlflow.log_params(grid_search.best_params_)
            mlflow.log_metric("accuracy", accuracy)
            mlflow.log_metric("train_samples", len(self.X_train))
            mlflow.log_metric("test_samples", len(self.X_test))
            
            # Log model
            mlflow.xgboost.log_model(self.xgb_model, "xgboost_model")
            
            print(f"XGBoost Accuracy: {accuracy:.4f}")
            print(f"Best parameters: {grid_search.best_params_}")
            
            # Classification report
            class_names = self.label_encoder.classes_
            report = classification_report(self.y_test, y_pred, target_names=class_names)
            print("Classification Report:")
            print(report)
            
            return accuracy
    
    def prepare_lstm_data(self):
        """Prepare data for LSTM model"""
        print("Preparing LSTM data...")
        
        # Tokenize text
        self.tokenizer.fit_on_texts(self.df['message'].fillna(''))
        
        # Convert to sequences
        sequences = self.tokenizer.texts_to_sequences(self.df['message'].fillna(''))
        max_length = 100
        X_seq = pad_sequences(sequences, maxlen=max_length)
        
        # Target variable (one-hot encoded)
        y_categorical = to_categorical(self.label_encoder.transform(self.df['incident_type']))
        
        # Split data
        X_train_seq, X_test_seq, y_train_cat, y_test_cat = train_test_split(
            X_seq, y_categorical, test_size=0.2, random_state=42
        )
        
        return X_train_seq, X_test_seq, y_train_cat, y_test_cat, max_length
    
    def train_lstm_model(self):
        """Train LSTM model for sequence analysis"""
        print("Training LSTM model...")
        
        X_train_seq, X_test_seq, y_train_cat, y_test_cat, max_length = self.prepare_lstm_data()
        
        with mlflow.start_run(run_name="lstm_training"):
            # Build LSTM model
            vocab_size = len(self.tokenizer.word_index) + 1
            embedding_dim = 100
            num_classes = len(self.label_encoder.classes_)
            
            model = Sequential([
                Embedding(vocab_size, embedding_dim, input_length=max_length),
                LSTM(128, dropout=0.2, recurrent_dropout=0.2, return_sequences=True),
                LSTM(64, dropout=0.2, recurrent_dropout=0.2),
                Dense(32, activation='relu'),
                Dropout(0.5),
                Dense(num_classes, activation='softmax')
            ])
            
            model.compile(
                optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy']
            )
            
            # Train model
            history = model.fit(
                X_train_seq, y_train_cat,
                batch_size=32,
                epochs=10,
                validation_data=(X_test_seq, y_test_cat),
                verbose=1
            )
            
            self.lstm_model = model
            
            # Evaluate
            loss, accuracy = model.evaluate(X_test_seq, y_test_cat, verbose=0)
            
            # Log metrics
            mlflow.log_param("vocab_size", vocab_size)
            mlflow.log_param("embedding_dim", embedding_dim)
            mlflow.log_param("max_length", max_length)
            mlflow.log_metric("lstm_accuracy", accuracy)
            mlflow.log_metric("lstm_loss", loss)
            
            print(f"LSTM Accuracy: {accuracy:.4f}")
            
            return accuracy
    
    def create_ensemble_model(self):
        """Create ensemble model combining XGBoost and LSTM"""
        print("Creating ensemble model...")
        
        # For simplicity, we'll use a weighted average approach
        # In production, you might train a meta-learner
        
        class EnsembleModel:
            def __init__(self, xgb_model, lstm_model, tokenizer, tfidf_vectorizer, 
                        scaler, label_encoder, weights=(0.7, 0.3)):
                self.xgb_model = xgb_model
                self.lstm_model = lstm_model
                self.tokenizer = tokenizer
                self.tfidf_vectorizer = tfidf_vectorizer
                self.scaler = scaler
                self.label_encoder = label_encoder
                self.weights = weights
                
            def predict_proba(self, messages, numerical_features=None):
                # XGBoost predictions
                if numerical_features is not None:
                    text_features = self.tfidf_vectorizer.transform(messages)
                    numerical_scaled = self.scaler.transform(numerical_features)
                    from scipy.sparse import hstack
                    X_combined = hstack([text_features, numerical_scaled])
                    xgb_proba = self.xgb_model.predict_proba(X_combined)
                else:
                    # Fallback to text-only prediction
                    text_features = self.tfidf_vectorizer.transform(messages)
                    xgb_proba = self.xgb_model.predict_proba(text_features)
                
                # LSTM predictions
                sequences = self.tokenizer.texts_to_sequences(messages)
                X_seq = pad_sequences(sequences, maxlen=100)
                lstm_proba = self.lstm_model.predict(X_seq)
                
                # Ensemble prediction
                ensemble_proba = (self.weights[0] * xgb_proba + 
                                self.weights[1] * lstm_proba)
                
                return ensemble_proba
            
            def predict(self, messages, numerical_features=None):
                proba = self.predict_proba(messages, numerical_features)
                return np.argmax(proba, axis=1)
        
        self.ensemble_model = EnsembleModel(
            self.xgb_model, self.lstm_model, self.tokenizer,
            self.tfidf_vectorizer, self.scaler, self.label_encoder
        )
        
        print("Ensemble model created successfully")
    
    def evaluate_ensemble(self):
        """Evaluate ensemble model performance"""
        print("Evaluating ensemble model...")
        
        # Prepare test data
        test_messages = []
        test_numerical = []
        
        for idx in range(len(self.y_test)):
            # Get original message
            test_idx = self.df.index[len(self.X_train) + idx]
            message = self.df.loc[test_idx, 'message']
            test_messages.append(message)
            
            # Get numerical features
            numerical_features = [
                self.df.loc[test_idx, 'cpu_usage'],
                self.df.loc[test_idx, 'memory_usage'],
                self.df.loc[test_idx, 'disk_usage'],
                self.df.loc[test_idx, 'response_time'],
                self.df.loc[test_idx, 'hour'],
                self.df.loc[test_idx, 'day_of_week'],
                self.df.loc[test_idx, 'is_weekend'],
                self.df.loc[test_idx, 'severity_score'],
                self.df.loc[test_idx, 'log_level_encoded'],
                self.df.loc[test_idx, 'service_encoded'],
                self.df.loc[test_idx, 'aws_service_encoded'],
                self.df.loc[test_idx, 'region_encoded'],
                self.df.loc[test_idx, 'environment_encoded']
            ]
            test_numerical.append(numerical_features)
        
        test_numerical = np.array(test_numerical)
        
        # Make predictions
        y_pred_ensemble = self.ensemble_model.predict(test_messages, test_numerical)
        accuracy = accuracy_score(self.y_test, y_pred_ensemble)
        
        print(f"Ensemble Accuracy: {accuracy:.4f}")
        
        # Classification report
        class_names = self.label_encoder.classes_
        report = classification_report(self.y_test, y_pred_ensemble, target_names=class_names)
        print("Ensemble Classification Report:")
        print(report)
        
        return accuracy
    
    def save_models(self, model_dir: str = 'models'):
        """Save trained models and preprocessors"""
        print(f"Saving models to {model_dir}...")
        
        os.makedirs(model_dir, exist_ok=True)
        
        # Save XGBoost model
        if self.xgb_model:
            self.xgb_model.save_model(f'{model_dir}/xgboost_model.json')
        
        # Save LSTM model
        if self.lstm_model:
            self.lstm_model.save(f'{model_dir}/lstm_model.h5')
        
        # Save preprocessors
        with open(f'{model_dir}/tfidf_vectorizer.pkl', 'wb') as f:
            pickle.dump(self.tfidf_vectorizer, f)
        
        with open(f'{model_dir}/label_encoder.pkl', 'wb') as f:
            pickle.dump(self.label_encoder, f)
        
        with open(f'{model_dir}/scaler.pkl', 'wb') as f:
            pickle.dump(self.scaler, f)
        
        with open(f'{model_dir}/tokenizer.pkl', 'wb') as f:
            pickle.dump(self.tokenizer, f)
        
        # Save ensemble model
        if self.ensemble_model:
            with open(f'{model_dir}/ensemble_model.pkl', 'wb') as f:
                pickle.dump(self.ensemble_model, f)
        
        # Save model metadata
        metadata = {
            'training_date': datetime.now().isoformat(),
            'num_classes': len(self.label_encoder.classes_),
            'class_names': self.label_encoder.classes_.tolist(),
            'feature_names': {
                'tfidf_features': self.tfidf_vectorizer.get_feature_names_out().tolist()[:100],  # First 100
                'numerical_features': [
                    'cpu_usage', 'memory_usage', 'disk_usage', 'response_time',
                    'hour', 'day_of_week', 'is_weekend', 'severity_score',
                    'log_level_encoded', 'service_encoded', 'aws_service_encoded',
                    'region_encoded', 'environment_encoded'
                ]
            }
        }
        
        with open(f'{model_dir}/model_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print("Models saved successfully")
    
    def run_full_pipeline(self):
        """Run the complete ML training pipeline"""
        print("Starting AI-RecoverOps ML Training Pipeline...")
        
        # Load and preprocess data
        self.load_and_preprocess_data()
        
        # Feature engineering
        self.feature_engineering()
        
        # Train models
        xgb_accuracy = self.train_xgboost_model()
        lstm_accuracy = self.train_lstm_model()
        
        # Create and evaluate ensemble
        self.create_ensemble_model()
        ensemble_accuracy = self.evaluate_ensemble()
        
        # Save models
        self.save_models()
        
        print("\n" + "="*50)
        print("TRAINING PIPELINE COMPLETED")
        print("="*50)
        print(f"XGBoost Accuracy: {xgb_accuracy:.4f}")
        print(f"LSTM Accuracy: {lstm_accuracy:.4f}")
        print(f"Ensemble Accuracy: {ensemble_accuracy:.4f}")
        print("="*50)
        
        return {
            'xgb_accuracy': xgb_accuracy,
            'lstm_accuracy': lstm_accuracy,
            'ensemble_accuracy': ensemble_accuracy
        }

def main():
    """Main training function"""
    pipeline = LogAnalysisMLPipeline()
    results = pipeline.run_full_pipeline()
    
    print("\nTraining completed successfully!")
    print("Models are ready for deployment.")

if __name__ == "__main__":
    main()