"""
ML Classifier Module
Predicts pathogenicity of genetic variants using machine learning
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle
import json
import os

class VariantPathogenicityClassifier:
    """ML model to predict variant pathogenicity"""
    
    def __init__(self):
        self.model = None
        self.feature_encoders = {}
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
        
    def extract_features(self, variant: dict) -> dict:
        """Extract features from variant for ML prediction"""
        features = {
            'consequence_score': self.consequence_severity.get(
                variant.get('consequence', 'Unknown'), 3
            ),
            'allele_frequency': float(variant.get('allele_frequency', 0.0)),
            'quality_score': float(variant.get('quality', 0)) if variant.get('quality') != '.' else 0,
            'is_coding': 1 if 'missense' in variant.get('consequence', '') or 
                            'nonsense' in variant.get('consequence', '') or
                            'frameshift' in variant.get('consequence', '') else 0,
            'gene_constraint': self._get_gene_constraint(variant.get('gene', 'Unknown'))
        }
        
        return features
    
    def _get_gene_constraint(self, gene: str) -> float:
        """Get gene constraint score"""
        high_constraint_genes = {
            'BRCA1': 0.95, 'BRCA2': 0.92, 'TP53': 0.98,
            'EGFR': 0.85, 'KRAS': 0.88, 'PTEN': 0.90,
            'ATM': 0.87, 'MLH1': 0.93, 'MSH2': 0.91
        }
        
        return high_constraint_genes.get(gene, 0.5)
    
    def train_model(self, training_data: pd.DataFrame = None):
        """Train Random Forest classifier"""
        if training_data is None:
            training_data = self._generate_training_data()
        
        X = []
        y = []
        
        for _, row in training_data.iterrows():
            features = self.extract_features(row.to_dict())
            X.append(list(features.values()))
            y.append(row['pathogenic'])
        
        X = np.array(X)
        y = np.array(y)
        
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        
        self.model.fit(X, y)
        
        print("Model trained successfully")
        print(f"Training samples: {len(X)}")
        
        return self.model
    
    def _generate_training_data(self) -> pd.DataFrame:
        """Generate simulated training data"""
        np.random.seed(42)
        
        pathogenic = []
        for _ in range(150):
            pathogenic.append({
                'gene': np.random.choice(['BRCA1', 'BRCA2', 'TP53', 'EGFR']),
                'consequence': np.random.choice(['frameshift_variant', 'nonsense_variant', 'splice_site_variant']),
                'allele_frequency': np.random.uniform(0, 0.001),
                'quality': np.random.uniform(40, 60),
                'pathogenic': 1
            })
        
        benign = []
        for _ in range(150):
            benign.append({
                'gene': np.random.choice(['BRCA1', 'TP53', 'EGFR', 'OTHER1', 'OTHER2']),
                'consequence': np.random.choice(['synonymous_variant', 'intron_variant', 'missense_variant']),
                'allele_frequency': np.random.uniform(0.01, 0.3),
                'quality': np.random.uniform(35, 55),
                'pathogenic': 0
            })
        
        df = pd.DataFrame(pathogenic + benign)
        return df
    
    def predict_pathogenicity(self, variant: dict) -> dict:
        """Predict if variant is pathogenic"""
        if self.model is None:
            self.train_model()
        
        features = self.extract_features(variant)
        X = np.array([list(features.values())])
        
        prediction = self.model.predict(X)[0]
        probability = self.model.predict_proba(X)[0]
        
        pathogenic_prob = probability[1]
        
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
            'confidence': round(max(probability), 3),
            'features_used': features,
            'clinical_significance': self._get_clinical_significance(classification, variant)
        }
        
        return result
    
    def _get_clinical_significance(self, classification: str, variant: dict) -> str:
        """Map classification to clinical recommendation"""
        gene = variant.get('gene', 'Unknown')
        
        significance_map = {
            "Pathogenic": f"Clinical action recommended. Variant in {gene} is associated with disease risk.",
            "Likely Pathogenic": f"Consider clinical correlation. Variant in {gene} may be disease-associated.",
            "Uncertain Significance": f"Insufficient evidence. Monitor literature for updates on {gene} variants.",
            "Likely Benign": f"No clinical action needed. Variant appears benign based on current evidence.",
            "Benign": f"No clinical concern. Common variant with no known pathogenicity."
        }
        
        return significance_map.get(classification, "Unknown clinical significance")
    
    def save_model(self, path: str = 'models/pathogenicity_model.pkl'):
        """Save trained model to disk"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'feature_encoders': self.feature_encoders,
                'consequence_severity': self.consequence_severity
            }, f)
        print(f"Model saved to {path}")
    
    def load_model(self, path: str = 'models/pathogenicity_model.pkl'):
        """Load trained model from disk"""
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.feature_encoders = data['feature_encoders']
            self.consequence_severity = data['consequence_severity']
        print(f"Model loaded from {path}")


if __name__ == "__main__":
    classifier = VariantPathogenicityClassifier()
    classifier.train_model()
    
    test_variant = {
        'id': 'chr17:43044295:T>C',
        'gene': 'BRCA1',
        'consequence': 'missense_variant',
        'allele_frequency': 0.0001,
        'quality': 55.0
    }
    
    result = classifier.predict_pathogenicity(test_variant)
    
    print("\nPrediction Result:")
    print(json.dumps(result, indent=2))
    
    classifier.save_model()
