"""
Ensemble Model System - Each Model Serves a Purpose
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score, classification_report, confusion_matrix
import pickle
import json
import os

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except:
    XGBOOST_AVAILABLE = False


class EnsembleVariantClassifier:
    """
    Three-model ensemble system:
    - Random Forest: Primary production model (explainable, robust)
    - Logistic Regression: Baseline reference (simple, interpretable)
    - XGBoost: Performance benchmark (high accuracy)
    """
    
    def __init__(self):
        self.rf_model = None
        self.lr_model = None
        self.xgb_model = None
        self.metrics = {}
        self.consequence_severity = {
            'frameshift_variant': 10, 'nonsense_variant': 9, 'splice_site_variant': 8,
            'missense_variant': 6, 'inframe_deletion': 5, 'inframe_insertion': 5,
            'synonymous_variant': 2, 'intron_variant': 1, 'Unknown': 3
        }
    
    def extract_features(self, variant):
        return {
            'consequence_score': self.consequence_severity.get(variant.get('consequence', 'Unknown'), 3),
            'allele_frequency': float(variant.get('allele_frequency', 0.0)),
            'quality_score': float(variant.get('quality', 0)) if variant.get('quality') != '.' else 0,
            'is_coding': 1 if any(x in variant.get('consequence', '') for x in ['missense', 'nonsense', 'frameshift']) else 0,
            'gene_constraint': self._get_gene_constraint(variant.get('gene', 'Unknown'))
        }
    
    def _get_gene_constraint(self, gene):
        gnomad_pli = {
            'BRCA1': 0.00, 'BRCA2': 0.00, 'TP53': 1.00, 'EGFR': 0.04, 'KRAS': 0.00, 'PTEN': 1.00,
            'ATM': 0.03, 'MLH1': 0.99, 'MSH2': 1.00, 'APC': 0.63, 'CDKN2A': 0.04, 'STK11': 1.00,
            'ROS1': 0.00, 'PDGFRA': 0.00, 'IDH2': 0.00, 'NRAS': 0.00, 'AKT1': 0.00,
            'CFTR': 1.00, 'HBB': 0.98, 'HEXA': 1.00, 'PKD1': 0.92, 'DMD': 1.00
        }
        return gnomad_pli.get(gene, 0.5)
    
    def _generate_training_data(self):
        np.random.seed(42)
        
        pathogenic = []
        genes = ['BRCA1', 'BRCA2', 'TP53', 'PTEN', 'MLH1', 'MSH2', 'CFTR', 'HBB', 'DMD']
        for _ in range(500):
            pathogenic.append({
                'gene': np.random.choice(genes),
                'consequence': np.random.choice(['frameshift_variant', 'nonsense_variant', 'splice_site_variant']),
                'allele_frequency': np.random.uniform(0, 0.0005),
                'quality': np.random.uniform(45, 60),
                'pathogenic': 1
            })
        
        benign = []
        for _ in range(500):
            benign.append({
                'gene': np.random.choice(genes + ['KRAS', 'NRAS', 'AKT1']),
                'consequence': np.random.choice(['synonymous_variant', 'intron_variant', 'missense_variant']),
                'allele_frequency': np.random.uniform(0.01, 0.4),
                'quality': np.random.uniform(35, 55),
                'pathogenic': 0
            })
        
        return pd.DataFrame(pathogenic + benign)
    
    def train_all_models(self):
        """Train all three models with 80/20 split"""
        
        data = self._generate_training_data()
        
        X = []
        y = []
        for _, row in data.iterrows():
            features = self.extract_features(row.to_dict())
            X.append(list(features.values()))
            y.append(row['pathogenic'])
        
        X = np.array(X)
        y = np.array(y)
        
        # 80/20 split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        print("\n" + "="*70)
        print("GENOINSIGHT ENSEMBLE MODEL TRAINING")
        print("="*70)
        print(f"Total samples: {len(X)}")
        print(f"Training: {len(X_train)} (80%)")
        print(f"Testing: {len(X_test)} (20%)")
        
        # Train Logistic Regression (Baseline)
        print("\n" + "-"*70)
        print("LOGISTIC REGRESSION - Baseline Reference Model")
        print("Purpose: Simple, interpretable baseline for comparison")
        print("-"*70)
        
        self.lr_model = LogisticRegression(random_state=42, max_iter=1000)
        self.lr_model.fit(X_train, y_train)
        
        lr_pred_proba = self.lr_model.predict_proba(X_test)[:, 1]
        lr_auc = roc_auc_score(y_test, self.lr_model.predict(X_test) if len(np.unique(y_test)) > 1 else 0)
        lr_acc = accuracy_score(y_test, self.lr_model.predict(X_test))
        
        print(f"AUC-ROC: {lr_auc:.3f}")
        print(f"Accuracy: {lr_acc:.3f}")
        
        self.metrics['logistic_regression'] = {
            'purpose': 'Baseline reference',
            'auc': float(lr_auc),
            'accuracy': float(lr_acc)
        }
        
        # Train Random Forest (Primary)
        print("\n" + "-"*70)
        print("RANDOM FOREST - Primary Production Model")
        print("Purpose: Explainable, robust, production-ready")
        print("-"*70)
        
        self.rf_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, class_weight='balanced')
        self.rf_model.fit(X_train, y_train)
        
        rf_pred = self.rf_model.predict(X_test)
        rf_pred_proba = self.rf_model.predict_proba(X_test)[:, 1]
        rf_auc = roc_auc_score(y_test, rf_pred_proba)
        rf_acc = accuracy_score(y_test, rf_pred)
        
        cm = confusion_matrix(y_test, rf_pred)
        sensitivity = cm[1,1] / (cm[1,1] + cm[1,0]) if (cm[1,1] + cm[1,0]) > 0 else 0
        specificity = cm[0,0] / (cm[0,0] + cm[0,1]) if (cm[0,0] + cm[0,1]) > 0 else 0
        
        print(f"AUC-ROC: {rf_auc:.3f}")
        print(f"Accuracy: {rf_acc:.3f}")
        print(f"Sensitivity: {sensitivity:.3f}")
        print(f"Specificity: {specificity:.3f}")
        
        features = ['Consequence', 'Allele Freq', 'Quality', 'Coding', 'Gene Constraint']
        print("\nFeature Importance:")
        for feat, imp in zip(features, self.rf_model.feature_importances_):
            print(f"  {feat:20s}: {imp:.3f}")
        
        self.metrics['random_forest'] = {
            'purpose': 'Primary production model',
            'auc': float(rf_auc),
            'accuracy': float(rf_acc),
            'sensitivity': float(sensitivity),
            'specificity': float(specificity),
            'feature_importance': {f: float(i) for f, i in zip(features, self.rf_model.feature_importances_)}
        }
        
        # Train XGBoost (Performance)
        if XGBOOST_AVAILABLE:
            print("\n" + "-"*70)
            print("XGBOOST - Performance Benchmark")
            print("Purpose: Check potential performance improvement")
            print("-"*70)
            
            self.xgb_model = XGBClassifier(n_estimators=100, max_depth=10, random_state=42, eval_metric='logloss', use_label_encoder=False)
            self.xgb_model.fit(X_train, y_train)
            
            xgb_pred_proba = self.xgb_model.predict_proba(X_test)[:, 1]
            xgb_auc = roc_auc_score(y_test, xgb_pred_proba)
            xgb_acc = accuracy_score(y_test, self.xgb_model.predict(X_test))
            
            print(f"AUC-ROC: {xgb_auc:.3f}")
            print(f"Accuracy: {xgb_acc:.3f}")
            
            self.metrics['xgboost'] = {
                'purpose': 'Performance benchmark',
                'auc': float(xgb_auc),
                'accuracy': float(xgb_acc)
            }
        
        # Summary
        print("\n" + "="*70)
        print("MODEL PURPOSES & RESULTS")
        print("="*70)
        for name, data in self.metrics.items():
            print(f"\n{name.upper()}:")
            print(f"  Purpose: {data['purpose']}")
            print(f"  AUC: {data['auc']:.3f} | Accuracy: {data['accuracy']:.3f}")
        print("="*70)
        
        # Save all
        self.save_all_models()
        
        return self.metrics
    
    def save_all_models(self):
        os.makedirs('models', exist_ok=True)
        
        # Save each model
        with open('models/random_forest.pkl', 'wb') as f:
            pickle.dump(self.rf_model, f)
        
        with open('models/logistic_regression.pkl', 'wb') as f:
            pickle.dump(self.lr_model, f)
        
        if self.xgb_model:
            with open('models/xgboost.pkl', 'wb') as f:
                pickle.dump(self.xgb_model, f)
        
        # Save metrics
        with open('models/ensemble_metrics.json', 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        print("\n✓ All models saved to models/ folder")
        print("✓ Metrics saved to models/ensemble_metrics.json")
    
    def predict_pathogenicity(self, variant, use_ensemble=False):
        """
        Predict using Random Forest (primary)
        If use_ensemble=True, average predictions from all models
        """
        if self.rf_model is None:
            self.train_all_models()
        
        features = self.extract_features(variant)
        X = np.array([list(features.values())])
        
        if use_ensemble and self.lr_model and self.xgb_model:
            # Ensemble: average probabilities
            rf_prob = self.rf_model.predict_proba(X)[0][1]
            lr_prob = self.lr_model.predict_proba(X)[0][1]
            xgb_prob = self.xgb_model.predict_proba(X)[0][1]
            
            pathogenic_prob = (rf_prob + lr_prob + xgb_prob) / 3
        else:
            # Use Random Forest only
            pathogenic_prob = self.rf_model.predict_proba(X)[0][1]
        
        if pathogenic_prob >= 0.9:
            classification = "Pathogenic"
        elif pathogenic_prob >= 0.7:
            classification = "Likely Pathogenic"
        elif pathogenic_prob >= 0.3:
            classification = "Uncertain Significance"
        elif pathogenic_prob >= 0.1:
            classification = "Likely Benign"
        else:
            classification = "Benign"
        
        result = {
            'variant_id': variant['id'],
            'classification': classification,
            'pathogenic_probability': round(pathogenic_prob, 3),
            'confidence': round(pathogenic_prob if pathogenic_prob > 0.5 else 1 - pathogenic_prob, 3),
            'features_used': features,
            'model_used': 'ensemble' if use_ensemble else 'random_forest'
        }
        
        return result


if __name__ == "__main__":
    print("Training ensemble system...")
    ensemble = EnsembleVariantClassifier()
    metrics = ensemble.train_all_models()
    
    print("\n\nAll models trained and saved!")
