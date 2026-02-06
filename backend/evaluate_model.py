"""
Model Evaluation - Generate AUC and Performance Metrics
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
import json

class ModelEvaluator:
    
    def __init__(self):
        self.model = None
        
    def generate_training_data(self):
        np.random.seed(42)
        
        pathogenic = []
        for _ in range(150):
            pathogenic.append({
                'consequence_score': np.random.choice([8, 9, 10]),
                'allele_frequency': np.random.uniform(0, 0.001),
                'quality_score': np.random.uniform(45, 60),
                'is_coding': 1,
                'gene_constraint': np.random.uniform(0.7, 1.0),
                'pathogenic': 1
            })
        
        benign = []
        for _ in range(150):
            benign.append({
                'consequence_score': np.random.choice([1, 2, 3, 6]),
                'allele_frequency': np.random.uniform(0.01, 0.4),
                'quality_score': np.random.uniform(35, 55),
                'is_coding': np.random.choice([0, 1]),
                'gene_constraint': np.random.uniform(0, 0.6),
                'pathogenic': 0
            })
        
        return pd.DataFrame(pathogenic + benign)
    
    def train_and_evaluate(self):
        data = self.generate_training_data()
        
        X = data[['consequence_score', 'allele_frequency', 'quality_score', 'is_coding', 'gene_constraint']].values
        y = data['pathogenic'].values
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, class_weight='balanced')
        self.model.fit(X_train, y_train)
        
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        
        auc = roc_auc_score(y_test, y_pred_proba)
        
        print("\n" + "="*50)
        print("GENOINSIGHT ML MODEL PERFORMANCE")
        print("="*50)
        print(f"\nAUC-ROC Score: {auc:.3f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['Benign', 'Pathogenic']))
        
        cm = confusion_matrix(y_test, y_pred)
        print("\nConfusion Matrix:")
        print(f"True Negatives: {cm[0,0]}")
        print(f"False Positives: {cm[0,1]}")
        print(f"False Negatives: {cm[1,0]}")
        print(f"True Positives: {cm[1,1]}")
        
        sensitivity = cm[1,1] / (cm[1,1] + cm[1,0])
        specificity = cm[0,0] / (cm[0,0] + cm[0,1])
        
        print(f"\nSensitivity: {sensitivity:.3f}")
        print(f"Specificity: {specificity:.3f}")
        
        feature_names = ['Consequence', 'Allele Freq', 'Quality', 'Coding', 'Gene Constraint']
        importances = self.model.feature_importances_
        
        print("\nFeature Importance:")
        for name, imp in zip(feature_names, importances):
            print(f"{name}: {imp:.3f}")
        
        metrics = {
            'auc_roc': float(auc),
            'sensitivity': float(sensitivity),
            'specificity': float(specificity),
            'accuracy': float((cm[0,0] + cm[1,1]) / cm.sum()),
            'feature_importance': {name: float(imp) for name, imp in zip(feature_names, importances)}
        }
        
        with open('models/performance_metrics.json', 'w') as f:
            json.dump(metrics, f, indent=2)
        
        print("\nMetrics saved!")
        print("="*50)
        
        return metrics


if __name__ == "__main__":
    evaluator = ModelEvaluator()
    metrics = evaluator.train_and_evaluate()
