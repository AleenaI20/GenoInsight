import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import os

class VariantPredictor:
    """ML models for variant pathogenicity prediction"""
    
    def __init__(self):
        self.rf_model = None
        self.lr_model = None
        self.xgb_model = None
        self.is_trained = False
        
    def generate_synthetic_training_data(self, n_samples=1000):
        """Generate synthetic variant features for demonstration"""
        np.random.seed(42)
        
        # Features: allele frequency, conservation score, functional impact, population frequency
        X = np.random.rand(n_samples, 10)
        
        # Labels: pathogenic (1) or benign (0)
        # Make pathogenic variants have lower allele freq and higher impact scores
        y = ((X[:, 0] < 0.3) & (X[:, 2] > 0.6)).astype(int)
        
        return X, y
    
    def train_models(self):
        """Train all three ML models"""
        print("🔬 Generating training data...")
        X, y = self.generate_synthetic_training_data(n_samples=2000)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        print("🤖 Training Random Forest...")
        self.rf_model = RandomForestClassifier(
            n_estimators=100, 
            max_depth=10, 
            random_state=42
        )
        self.rf_model.fit(X_train, y_train)
        rf_pred = self.rf_model.predict(X_test)
        
        print("🤖 Training Logistic Regression...")
        self.lr_model = LogisticRegression(
            max_iter=1000, 
            random_state=42
        )
        self.lr_model.fit(X_train, y_train)
        lr_pred = self.lr_model.predict(X_test)
        
        # Simulate XGBoost with Random Forest (since XGBoost might not be installed)
        print("🤖 Training XGBoost (simulated)...")
        self.xgb_model = RandomForestClassifier(
            n_estimators=150, 
            max_depth=12, 
            random_state=43
        )
        self.xgb_model.fit(X_train, y_train)
        xgb_pred = self.xgb_model.predict(X_test)
        
        # Calculate metrics
        print("\n📊 Model Performance:")
        print(f"Random Forest - Accuracy: {accuracy_score(y_test, rf_pred):.3f}")
        print(f"Logistic Regression - Accuracy: {accuracy_score(y_test, lr_pred):.3f}")
        print(f"XGBoost - Accuracy: {accuracy_score(y_test, xgb_pred):.3f}")
        
        self.is_trained = True
        print("✅ All models trained successfully!\n")
        
    def predict(self, variant_features):
        """Predict pathogenicity for a variant"""
        if not self.is_trained:
            self.train_models()
            
        if isinstance(variant_features, list):
            variant_features = np.array(variant_features).reshape(1, -1)
            
        predictions = {
            'random_forest': float(self.rf_model.predict_proba(variant_features)[0][1]),
            'logistic_regression': float(self.lr_model.predict_proba(variant_features)[0][1]),
            'xgboost': float(self.xgb_model.predict_proba(variant_features)[0][1])
        }
        
        predictions['consensus'] = np.mean(list(predictions.values()))
        
        return predictions

if __name__ == '__main__':
    predictor = VariantPredictor()
    predictor.train_models()
