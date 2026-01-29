"""
Clinical Annotator Module - With gnomAD population data
"""

import json
from typing import Dict, List, Any
import sys
import os

# Import gnomAD data
sys.path.insert(0, os.path.dirname(__file__))
from gnomad_data import get_population_frequency

class ClinicalAnnotator:
    
    def __init__(self):
        self.drug_gene_db = self._load_pharmacogenomics_db()
        self.disease_associations = self._load_disease_associations()
    
    def _load_pharmacogenomics_db(self):
        return {
            'BRCA1': {'drugs': ['Olaparib', 'Talazoparib', 'Rucaparib'], 'indication': 'PARP inhibitors for BRCA-mutated cancers', 'evidence_level': 'FDA Approved', 'response': 'Increased sensitivity to PARP inhibitors'},
            'BRCA2': {'drugs': ['Olaparib', 'Talazoparib'], 'indication': 'PARP inhibitors for BRCA-mutated cancers', 'evidence_level': 'FDA Approved', 'response': 'Increased sensitivity to PARP inhibitors'},
            'EGFR': {'drugs': ['Gefitinib', 'Erlotinib', 'Osimertinib'], 'indication': 'EGFR-mutated non-small cell lung cancer', 'evidence_level': 'FDA Approved', 'response': 'Targeted therapy - improved outcomes'},
            'TP53': {'drugs': ['Clinical trial consideration'], 'indication': 'Li-Fraumeni syndrome surveillance', 'evidence_level': 'Clinical Guidelines', 'response': 'Enhanced cancer screening recommended'}
        }
    
    def _load_disease_associations(self):
        return {
            'BRCA1': {'diseases': ['Hereditary Breast and Ovarian Cancer Syndrome'], 'inheritance': 'Autosomal Dominant', 'cancer_risks': {'Breast Cancer': '55-85% lifetime risk', 'Ovarian Cancer': '15-45% lifetime risk'}, 'screening': 'Annual MRI/mammography starting age 25-30'},
            'BRCA2': {'diseases': ['Hereditary Breast and Ovarian Cancer Syndrome'], 'inheritance': 'Autosomal Dominant', 'cancer_risks': {'Breast Cancer': '45-85% lifetime risk', 'Ovarian Cancer': '10-30% lifetime risk'}, 'screening': 'Annual MRI/mammography'},
            'TP53': {'diseases': ['Li-Fraumeni Syndrome'], 'inheritance': 'Autosomal Dominant', 'cancer_risks': {'Various Cancers': '90% lifetime cancer risk'}, 'screening': 'Comprehensive cancer screening protocol'},
            'EGFR': {'diseases': ['Non-Small Cell Lung Cancer (somatic)'], 'inheritance': 'Somatic mutation', 'cancer_risks': {'Lung Cancer': 'Targetable mutation'}, 'screening': 'Tumor testing recommended'}
        }
    
    def annotate_variant(self, variant, ml_prediction, patient_ancestry='Unknown'):
        gene = variant.get('gene', 'Unknown')
        variant_id = variant.get('id')
        
        # Get population-specific frequency from gnomAD
        pop_freq = get_population_frequency(variant_id, patient_ancestry)
        
        annotation = {
            'variant': variant,
            'ml_classification': ml_prediction,
            'pharmacogenomics': self._get_drug_recommendations(gene),
            'disease_association': self._get_disease_info(gene),
            'clinical_actionability': self._assess_actionability(variant, ml_prediction),
            'patient_impact': self._generate_patient_summary(gene, ml_prediction),
            'population_data': {
                'patient_ancestry': patient_ancestry,
                'allele_frequency_in_population': pop_freq,
                'gnomad_integrated': variant_id in ['chr17:43044295:T>C', 'chr13:32315474:G>T', 'chr7:55242464:G>A', 'chr2:67890:C>T', 'chr12:25398285:C>G', 'chr10:89624227:T>A']
            }
        }
        
        return annotation
    
    def _get_drug_recommendations(self, gene):
        if gene in self.drug_gene_db:
            return self.drug_gene_db[gene]
        return {'drugs': [], 'indication': 'No specific drug interactions known', 'evidence_level': 'N/A'}
    
    def _get_disease_info(self, gene):
        if gene in self.disease_associations:
            return self.disease_associations[gene]
        return {'diseases': ['Unknown/Not in database'], 'inheritance': 'Unknown', 'cancer_risks': {}, 'screening': 'Consult genetic counselor'}
    
    def _assess_actionability(self, variant, ml_prediction):
        classification = ml_prediction.get('classification', 'Uncertain Significance')
        gene = variant.get('gene', 'Unknown')
        actionable_genes = ['BRCA1', 'BRCA2', 'TP53', 'EGFR', 'KRAS']
        
        if classification in ['Pathogenic', 'Likely Pathogenic'] and gene in actionable_genes:
            return "HIGH - Clinical action recommended"
        elif classification in ['Pathogenic', 'Likely Pathogenic']:
            return "MODERATE - Consider genetic counseling"
        elif classification == 'Uncertain Significance':
            return "LOW - Monitoring recommended"
        else:
            return "MINIMAL - No immediate action required"
    
    def _generate_patient_summary(self, gene, ml_prediction):
        classification = ml_prediction.get('classification', 'Uncertain')
        summaries = {
            'Pathogenic': f"A significant genetic change was found in your {gene} gene that increases health risks.",
            'Likely Pathogenic': f"A genetic change in your {gene} gene was identified that likely affects your health.",
            'Uncertain Significance': f"A genetic change in {gene} was found, but more research is needed.",
            'Likely Benign': f"A genetic change in {gene} is unlikely to affect your health.",
            'Benign': f"A common genetic variation in {gene} was found with no health concerns."
        }
        return summaries.get(classification, "Please discuss with your healthcare provider.")
    
    def generate_clinical_report(self, annotations):
        actionable_variants = [a for a in annotations if a['ml_classification']['classification'] in ['Pathogenic', 'Likely Pathogenic']]
        
        report = {
            'summary': {
                'total_variants': len(annotations),
                'pathogenic': len([a for a in annotations if 'Pathogenic' in a['ml_classification']['classification']]),
                'uncertain': len([a for a in annotations if 'Uncertain' in a['ml_classification']['classification']]),
                'benign': len([a for a in annotations if 'Benign' in a['ml_classification']['classification']])
            },
            'priority_variants': sorted(actionable_variants, key=lambda x: x['ml_classification']['pathogenic_probability'], reverse=True)[:5],
            'genetic_counseling_indicated': len(actionable_variants) > 0
        }
        
        return report


if __name__ == "__main__":
    annotator = ClinicalAnnotator()
    
    test_variant = {'id': 'chr17:43044295:T>C', 'gene': 'BRCA1', 'consequence': 'missense_variant', 'allele_frequency': 0.0001, 'quality': 55.0}
    test_ml_pred = {'variant_id': 'chr17:43044295:T>C', 'classification': 'Likely Pathogenic', 'pathogenic_probability': 0.82, 'confidence': 0.82}
    
    annotation = annotator.annotate_variant(test_variant, test_ml_pred, 'East Asian')
    
    print("Clinical Annotation with gnomAD population data:")
    print(json.dumps(annotation, indent=2))
