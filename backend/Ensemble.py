"""
Ensemble Variant Pathogenicity Classifier
----------------------------------------
Prototype ensemble ML system for genomic variant prioritization.
Uses clinically interpretable features and population-aware logic.

NOTE:
- Uses simulated ClinVar-style data for demonstration purposes
- For research use only; not a diagnostic system
"""

import numpy as np
import pandas as pd
import pickle
import json
import os

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    roc_auc_score,
    accuracy_score,
    confusion_matrix
)
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False


class EnsembleVariantClassifier:
    """
    Three-model ensemble system:
    - Random Forest: Primary explainable production model
    - Logistic Regression: Interpretable baseline
    - XGBoost: Performance benchmark
    """

    def __init__(self):
        self.rf_model = None
        self.lr_model = None
        self.xgb_model = None
        self.metrics = {}

        # Consequence severity mapping (ACMG-inspired)
        self.consequence_severity = {
            'frameshift_variant': 10,
            'nonsense_variant': 9,
            'splice_site_variant': 8,
            'missense_variant': 6,
            'inframe_deletion': 5,
            'inframe_insertion': 5,
            'synonymous_variant': 2,
            'intron_variant': 1,
            'Unknown': 3
        }

    # ------------------------------------------------------------------
    # Feature Engineering
    # ------------------------------------------------------------------
    def extract_features(self, variant: dict) -> dict:
        """
        Extract clinically interpretable features from a variant.
        """
        return {
            'consequence_score': self.consequence_severity.get(
                variant.get('consequence', 'Unknown'), 3
            ),
            'allele_frequency': float(variant.get('allele_frequency', 0.0)),
            'quality_score': float(variant.get('quality', 0))
            if variant.get('quality') != '.' else 0,
            'is_coding': int(
                any(x in variant.get('consequence', '')
                    for x in ['missense', 'nonsense', 'frameshift'])
            ),
            'gene_constraint': self._get_gene_constraint(
                variant.get('gene', 'Unknown')
            )
        }

    def _get_gene_constraint(self, gene: str) -> float:
        """
        Approximate gnomAD pLI-style gene constraint scores.
        """
        gnomad_pli = {
            'BRCA1': 0.00, 'BRCA2': 0.00, 'TP53': 1.00, 'PTEN': 1.00,
            'MLH1': 0.99, 'MSH2': 1.00, 'CFTR': 1.00, 'HBB': 0.98,
            'DMD': 1.00, 'EGFR': 0.04, 'KRAS': 0.00, 'NRAS': 0.00,
            'AKT1': 0.00
        }
        return gnomad_pli.get(gene, 0.5)

    # ------------------------------------------------------------------
    # Synthetic Training Data (Prototype Only)
    # ------------------------------------------------------------------
    def _generate_training_data(self) -> pd.DataFrame:
        """
        Generate simulated ClinVar-style training data.
        """
        np.random.seed(42)
        genes = ['BRCA1', 'BRCA2', 'TP53', 'PTEN',
                 'MLH1', 'MSH2', 'CFTR', 'HBB', 'DMD']

        pathogenic = [{
            'gene': np.random.choice(genes),
            'consequence': np.random.choice(
                ['frameshift_variant', 'nonsense_variant', 'splice_site_variant']
            ),
            'allele_frequency': np.random.uniform(0, 0.0005),
            'quality': np.random.uniform(45, 60),
            'pathogenic': 1
        } for _ in range(500)]

        benign = [{
            'gene': np.random.choice(genes + ['KRAS', 'NRAS', 'AKT1']),
            'consequence': np.random.choice(
                ['synonymous_variant', 'intron_variant', 'missense_variant']
            ),
            'allele_frequency': np.random.uniform(0.01, 0.4),
            'quality': np.random.uniform(35, 55),
            'pathogenic': 0
        } for _ in range(500)]

        return pd.DataFrame(pathogenic + benign)

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------
    def train_all_models(self):
        """
        Train all models using an 80/20 stratified split.
        """
        data = self._generate_training_data()

        X, y = [], []
        for _, row in data.iterrows():
            feats = self.extract_features(row.to_dict())
            X.append(list(feats.values()))
            y.append(row['pathogenic'])

        X = np.array(X)
        y = np.array(y)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, stratify=y, random_state=42
        )

        # ---------------- Logistic Regression ----------------
        self.lr_model = Pipeline([
            ('scaler', StandardScaler()),
            ('lr', LogisticRegression(max_iter=1000, random_state=42))
        ])
        self.lr_model.fit(X_train, y_train)

        lr_proba = self.lr_model.predict_proba(X_test)[:, 1]
        lr_auc = roc_auc_score(y_test, lr_proba)
        lr_acc = accuracy_score(y_test, self.lr_model.predict(X_test))

        self.metrics['logistic_regression'] = {
            'purpose': 'Interpretable baseline',
            'auc': float(lr_auc),
            'accuracy': float(lr_acc)
        }

        # ---------------- Random Forest ----------------
        self.rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            class_weight='balanced',
            random_state=42
        )
        self.rf_model.fit(X_train, y_train)

        rf_pred = self.rf_model.predict(X_test)
        rf_proba = self.rf_model.predict_proba(X_test)[:, 1]
        rf_auc = roc_auc_score(y_test, rf_proba)
        rf_acc = accuracy_score(y_test, rf_pred)

        cm = confusion_matrix(y_test, rf_pred)
        sensitivity = cm[1, 1] / (cm[1, 1] + cm[1, 0])
        specificity = cm[0, 0] / (cm[0, 0] + cm[0, 1])

        self.metrics['random_forest'] = {
            'purpose': 'Primary explainable model',
            'auc': float(rf_auc),
            'accuracy': float(rf_acc),
            'sensitivity': float(sensitivity),
            'specificity': float(specificity),
            'feature_importance': dict(
                zip(
                    ['consequence', 'allele_freq', 'quality', 'coding', 'constraint'],
                    map(float, self.rf_model.feature_importances_)
                )
            )
        }

        # ---------------- XGBoost ----------------
        if XGBOOST_AVAILABLE:
            scale_pos_weight = len(y_train[y_train == 0]) / len(y_train[y_train == 1])
            self.xgb_model = XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                scale_pos_weight=scale_pos_weight,
                eval_metric='logloss',
                random_state=42
            )
            self.xgb_model.fit(X_train, y_train)

            xgb_proba = self.xgb_model.predict_proba(X_test)[:, 1]
            xgb_auc = roc_auc_score(y_test, xgb_proba)
            xgb_acc = accuracy_score(y_test, self.xgb_model.predict(X_test))

            self.metrics['xgboost'] = {
                'purpose': 'Performance benchmark',
                'auc': float(xgb_auc),
                'accuracy': float(xgb_acc)
            }

        self.save_all_models()
        return self.metrics

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------
    def predict_pathogenicity(self, variant: dict, use_ensemble=False) -> dict:
        """
        Predict pathogenicity using Random Forest or ensemble averaging.
        """
        if self.rf_model is None:
            self.train_all_models()

        features = self.extract_features(variant)
        X = np.array([list(features.values())])

        if use_ensemble and self.lr_model and self.xgb_model:
            probs = [
                self.rf_model.predict_proba(X)[0][1],
                self.lr_model.predict_proba(X)[0][1],
                self.xgb_model.predict_proba(X)[0][1]
            ]
            pathogenic_prob = float(np.mean(probs))
            model_used = 'ensemble'
        else:
            pathogenic_prob = float(self.rf_model.predict_proba(X)[0][1])
            model_used = 'random_forest'

        if pathogenic_prob >= 0.9:
            label = "Pathogenic"
        elif pathogenic_prob >= 0.7:
            label = "Likely Pathogenic"
        elif pathogenic_prob >= 0.3:
            label = "Uncertain Significance"
        elif pathogenic_prob >= 0.1:
            label = "Likely Benign"
        else:
            label = "Benign"

        return {
            'variant_id': variant.get('id'),
            'classification': label,
            'pathogenic_probability': round(pathogenic_prob, 3),
            'confidence': round(max(pathogenic_prob, 1 - pathogenic_prob), 3),
            'model_used': model_used,
            'features_used': features
        }

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def save_all_models(self):
        os.makedirs('models', exist_ok=True)

        pickle.dump(self.rf_model, open('models/random_forest.pkl', 'wb'))
        pickle.dump(self.lr_model, open('models/logistic_regression.pkl', 'wb'))

        if self.xgb_model:
            pickle.dump(self.xgb_model, open('models/xgboost.pkl', 'wb'))

        json.dump(self.metrics, open('models/ensemble_metrics.json', 'w'), indent=2)


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
if __name__ == "__main__":
    ensemble = EnsembleVariantClassifier()
    metrics = ensemble.train_all_models()
    print("\n✓ Ensemble training complete")
