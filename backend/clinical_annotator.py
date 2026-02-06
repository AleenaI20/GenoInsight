"""
Clinical Annotator Module - Expanded for Rare Diseases
With gnomAD population data
"""

import json
from typing import Dict, List, Any
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from gnomad_data import get_population_frequency

class ClinicalAnnotator:
    
    def __init__(self):
        self.drug_gene_db = self._load_pharmacogenomics_db()
        self.disease_associations = self._load_disease_associations()
    
    def _load_pharmacogenomics_db(self):
        return {
            # Cancer genes
            'BRCA1': {'drugs': ['Olaparib', 'Talazoparib', 'Rucaparib'], 'indication': 'PARP inhibitors for BRCA-mutated cancers', 'evidence_level': 'FDA Approved'},
            'BRCA2': {'drugs': ['Olaparib', 'Talazoparib'], 'indication': 'PARP inhibitors for BRCA-mutated cancers', 'evidence_level': 'FDA Approved'},
            'EGFR': {'drugs': ['Osimertinib', 'Gefitinib', 'Erlotinib'], 'indication': 'EGFR-mutated NSCLC', 'evidence_level': 'FDA Approved'},
            'TP53': {'drugs': ['Clinical trial consideration'], 'indication': 'Li-Fraumeni syndrome', 'evidence_level': 'Clinical Guidelines'},
            
            # Rare disease pharmacogenomics
            'CFTR': {'drugs': ['Ivacaftor', 'Lumacaftor', 'Tezacaftor'], 'indication': 'Cystic fibrosis with specific mutations', 'evidence_level': 'FDA Approved'},
            'HBB': {'drugs': ['Hydroxyurea', 'Voxelotor', 'Crizanlizumab'], 'indication': 'Sickle cell disease', 'evidence_level': 'FDA Approved'},
            'F8': {'drugs': ['Factor VIII replacement'], 'indication': 'Hemophilia A', 'evidence_level': 'Standard of Care'},
            'GBA': {'drugs': ['Eliglustat', 'Imiglucerase'], 'indication': 'Gaucher disease', 'evidence_level': 'FDA Approved'}
        }
    
    def _load_disease_associations(self):
        return {
            # Cancer genes
            'BRCA1': {'diseases': ['Hereditary Breast and Ovarian Cancer'], 'inheritance': 'Autosomal Dominant', 'prevalence': '1 in 400', 'category': 'Cancer Predisposition'},
            'BRCA2': {'diseases': ['Hereditary Breast and Ovarian Cancer'], 'inheritance': 'Autosomal Dominant', 'prevalence': '1 in 400', 'category': 'Cancer Predisposition'},
            'TP53': {'diseases': ['Li-Fraumeni Syndrome'], 'inheritance': 'Autosomal Dominant', 'prevalence': 'Rare', 'category': 'Cancer Predisposition'},
            'EGFR': {'diseases': ['Non-Small Cell Lung Cancer (somatic)'], 'inheritance': 'Somatic', 'prevalence': '15% of NSCLC', 'category': 'Oncology'},
            'MLH1': {'diseases': ['Lynch Syndrome'], 'inheritance': 'Autosomal Dominant', 'prevalence': '1 in 300', 'category': 'Cancer Predisposition'},
            'MSH2': {'diseases': ['Lynch Syndrome'], 'inheritance': 'Autosomal Dominant', 'prevalence': '1 in 300', 'category': 'Cancer Predisposition'},
            
            # Rare diseases
            'CFTR': {'diseases': ['Cystic Fibrosis'], 'inheritance': 'Autosomal Recessive', 'prevalence': '1 in 3,500 (European)', 'category': 'Rare Disease'},
            'HBB': {'diseases': ['Sickle Cell Disease', 'Beta-Thalassemia'], 'inheritance': 'Autosomal Recessive', 'prevalence': '1 in 365 (African American)', 'category': 'Rare Disease'},
            'HEXA': {'diseases': ['Tay-Sachs Disease'], 'inheritance': 'Autosomal Recessive', 'prevalence': '1 in 3,600 (Ashkenazi Jewish)', 'category': 'Rare Disease'},
            'PKD1': {'diseases': ['Polycystic Kidney Disease'], 'inheritance': 'Autosomal Dominant', 'prevalence': '1 in 1,000', 'category': 'Rare Disease'},
            'DMD': {'diseases': ['Duchenne Muscular Dystrophy'], 'inheritance': 'X-linked Recessive', 'prevalence': '1 in 5,000 males', 'category': 'Rare Disease'},
            'FMR1': {'diseases': ['Fragile X Syndrome'], 'inheritance': 'X-linked Dominant', 'prevalence': '1 in 4,000 males', 'category': 'Rare Disease'},
            'GBA': {'diseases': ['Gaucher Disease'], 'inheritance': 'Autosomal Recessive', 'prevalence': '1 in 40,000', 'category': 'Rare Disease'},
            'F8': {'diseases': ['Hemophilia A'], 'inheritance': 'X-linked Recessive', 'prevalence': '1 in 5,000 males', 'category': 'Rare Disease'},
            'PAH': {'diseases': ['Phenylketonuria (PKU)'], 'inheritance': 'Autosomal Recessive', 'prevalence': '1 in 10,000', 'category': 'Rare Disease'},
            'SMN1': {'diseases': ['Spinal Muscular Atrophy'], 'inheritance': 'Autosomal Recessive', 'prevalence': '1 in 10,000', 'category': 'Rare Disease'}
        }
    
    def annotate_variant(self, variant, ml_prediction, patient_ancestry='Unknown'):
        gene = variant.get('gene', 'Unknown')
        variant_id = variant.get('id')
        
        # Get population-specific frequency
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
                'gnomad_integrated': True
            }
        }
        
        return annotation
    
    def _get_drug_recommendations(self, gene):
        if gene in self.drug_gene_db:
            return self.drug_gene_db[gene]
        return {'drugs': [], 'indication': 'No specific therapies', 'evidence_level': 'N/A'}
    
    def _get_disease_info(self, gene):
        if gene in self.disease_associations:
            return self.disease_associations[gene]
        return {'diseases': ['Unknown'], 'inheritance': 'Unknown', 'prevalence': 'Unknown', 'category': 'Unknown'}
    
    def _assess_actionability(self, variant, ml_prediction):
        classification = ml_prediction.get('classification', 'Uncertain Significance')
        gene = variant.get('gene', 'Unknown')
        actionable_genes = ['BRCA1', 'BRCA2', 'TP53', 'EGFR', 'CFTR', 'HBB', 'F8', 'GBA']
        
        if classification in ['Pathogenic', 'Likely Pathogenic'] and gene in actionable_genes:
            return "HIGH - Clinical action recommended"
        elif classification in ['Pathogenic', 'Likely Pathogenic']:
            return "MODERATE - Genetic counseling"
        else:
            return "LOW - Monitoring"
    
    def _generate_patient_summary(self, gene, ml_prediction):
        classification = ml_prediction.get('classification', 'Uncertain')
        summaries = {
            'Pathogenic': f"Significant genetic change in {gene} gene increases health risks.",
            'Likely Pathogenic': f"Genetic change in {gene} likely affects health.",
            'Uncertain Significance': f"Genetic change in {gene} needs more research.",
            'Likely Benign': f"Genetic change in {gene} unlikely to affect health.",
            'Benign': f"Common variation in {gene} with no health concerns."
        }
        return summaries.get(classification, "Discuss with healthcare provider.")
    
    def generate_clinical_report(self, annotations):
        actionable = [a for a in annotations if a['ml_classification']['classification'] in ['Pathogenic', 'Likely Pathogenic']]
        
        return {
            'summary': {
                'total_variants': len(annotations),
                'pathogenic': len([a for a in annotations if 'Pathogenic' in a['ml_classification']['classification']]),
                'uncertain': len([a for a in annotations if 'Uncertain' in a['ml_classification']['classification']]),
                'benign': len([a for a in annotations if 'Benign' in a['ml_classification']['classification']])
            },
            'priority_variants': sorted(actionable, key=lambda x: x['ml_classification']['pathogenic_probability'], reverse=True)[:5],
            'genetic_counseling_indicated': len(actionable) > 0
        }


if __name__ == "__main__":
    annotator = ClinicalAnnotator()
    
    test_variant = {'id': 'chr17:43044295:T>C', 'gene': 'BRCA1', 'consequence': 'missense_variant', 'allele_frequency': 0.0001, 'quality': 55.0}
    test_ml = {'variant_id': 'chr17:43044295:T>C', 'classification': 'Likely Pathogenic', 'pathogenic_probability': 0.82}
    
    annotation = annotator.annotate_variant(test_variant, test_ml, 'East Asian')
    print("Annotation with rare disease coverage:")
    print(json.dumps(annotation, indent=2))
