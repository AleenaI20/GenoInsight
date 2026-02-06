"""
Clinical Annotator Module - Expanded for Rare Diseases
With gnomAD population data, validation, and clinical enhancements
"""

import json
from typing import Dict, List, Any, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from gnomad_data import get_population_frequency


class ClinicalAnnotator:
    
    def __init__(self):
        self.drug_gene_db = self._load_pharmacogenomics_db()
        self.disease_associations = self._load_disease_associations()
    
    def _load_pharmacogenomics_db(self) -> Dict[str, Dict[str, Any]]:
        """Load pharmacogenomics database - FDA-approved drug-gene pairs"""
        return {
            # Cancer genes
            'BRCA1': {'drugs': ['Olaparib', 'Talazoparib', 'Rucaparib'], 'indication': 'PARP inhibitors for BRCA-mutated cancers', 'evidence_level': 'FDA Approved'},
            'BRCA2': {'drugs': ['Olaparib', 'Talazoparib'], 'indication': 'PARP inhibitors for BRCA-mutated cancers', 'evidence_level': 'FDA Approved'},
            'EGFR': {'drugs': ['Osimertinib', 'Gefitinib', 'Erlotinib'], 'indication': 'EGFR-mutated NSCLC', 'evidence_level': 'FDA Approved'},
            'TP53': {'drugs': ['Clinical trial consideration'], 'indication': 'Li-Fraumeni syndrome surveillance', 'evidence_level': 'Clinical Guidelines'},
            'KRAS': {'drugs': ['Sotorasib', 'Adagrasib'], 'indication': 'KRAS G12C-mutated cancers', 'evidence_level': 'FDA Approved'},
            'MLH1': {'drugs': ['Immunotherapy consideration'], 'indication': 'MSI-high tumors', 'evidence_level': 'Clinical Guidelines'},
            'MSH2': {'drugs': ['Immunotherapy consideration'], 'indication': 'MSI-high tumors', 'evidence_level': 'Clinical Guidelines'},
            
            # Rare disease pharmacogenomics
            'CFTR': {'drugs': ['Ivacaftor', 'Lumacaftor', 'Tezacaftor'], 'indication': 'CF with specific CFTR mutations', 'evidence_level': 'FDA Approved'},
            'HBB': {'drugs': ['Hydroxyurea', 'Voxelotor', 'Crizanlizumab'], 'indication': 'Sickle cell disease', 'evidence_level': 'FDA Approved'},
            'F8': {'drugs': ['Factor VIII replacement therapy'], 'indication': 'Hemophilia A', 'evidence_level': 'Standard of Care'},
            'GBA': {'drugs': ['Eliglustat', 'Imiglucerase'], 'indication': 'Gaucher disease', 'evidence_level': 'FDA Approved'},
            'DMD': {'drugs': ['Eteplirsen', 'Golodirsen'], 'indication': 'Duchenne MD (exon-specific)', 'evidence_level': 'FDA Approved'},
            'SMN1': {'drugs': ['Nusinersen', 'Onasemnogene'], 'indication': 'Spinal muscular atrophy', 'evidence_level': 'FDA Approved'}
        }
    
    def _load_disease_associations(self) -> Dict[str, Dict[str, Any]]:
        """Load gene-disease associations"""
        return {
            # Cancer genes
            'BRCA1': {'diseases': ['Hereditary Breast and Ovarian Cancer'], 'inheritance': 'Autosomal Dominant', 'prevalence': '1 in 400', 'category': 'Cancer Predisposition', 'origin': 'Germline'},
            'BRCA2': {'diseases': ['Hereditary Breast and Ovarian Cancer'], 'inheritance': 'Autosomal Dominant', 'prevalence': '1 in 400', 'category': 'Cancer Predisposition', 'origin': 'Germline'},
            'TP53': {'diseases': ['Li-Fraumeni Syndrome'], 'inheritance': 'Autosomal Dominant', 'prevalence': 'Rare (<1 in 5,000)', 'category': 'Cancer Predisposition', 'origin': 'Germline or Somatic'},
            'EGFR': {'diseases': ['Non-Small Cell Lung Cancer'], 'inheritance': 'Somatic', 'prevalence': '15% of NSCLC', 'category': 'Oncology', 'origin': 'Somatic'},
            'KRAS': {'diseases': ['Colorectal/Lung Cancer'], 'inheritance': 'Somatic', 'prevalence': '30-40% CRC', 'category': 'Oncology', 'origin': 'Somatic'},
            'MLH1': {'diseases': ['Lynch Syndrome'], 'inheritance': 'Autosomal Dominant', 'prevalence': '1 in 300', 'category': 'Cancer Predisposition', 'origin': 'Germline'},
            'MSH2': {'diseases': ['Lynch Syndrome'], 'inheritance': 'Autosomal Dominant', 'prevalence': '1 in 300', 'category': 'Cancer Predisposition', 'origin': 'Germline'},
            'PTEN': {'diseases': ['PTEN Hamartoma Syndrome'], 'inheritance': 'Autosomal Dominant', 'prevalence': 'Rare', 'category': 'Cancer Predisposition', 'origin': 'Germline'},
            'ATM': {'diseases': ['Ataxia-Telangiectasia'], 'inheritance': 'Autosomal Recessive', 'prevalence': '1 in 40,000', 'category': 'Cancer Predisposition', 'origin': 'Germline'},
            
            # Rare diseases
            'CFTR': {'diseases': ['Cystic Fibrosis'], 'inheritance': 'Autosomal Recessive', 'prevalence': '1 in 3,500 (European)', 'category': 'Rare Disease', 'origin': 'Germline'},
            'HBB': {'diseases': ['Sickle Cell Disease', 'Beta-Thalassemia'], 'inheritance': 'Autosomal Recessive', 'prevalence': '1 in 365 (African American)', 'category': 'Rare Disease', 'origin': 'Germline'},
            'HEXA': {'diseases': ['Tay-Sachs Disease'], 'inheritance': 'Autosomal Recessive', 'prevalence': '1 in 3,600 (Ashkenazi Jewish)', 'category': 'Rare Disease', 'origin': 'Germline'},
            'PKD1': {'diseases': ['Polycystic Kidney Disease'], 'inheritance': 'Autosomal Dominant', 'prevalence': '1 in 1,000', 'category': 'Rare Disease', 'origin': 'Germline'},
            'DMD': {'diseases': ['Duchenne Muscular Dystrophy'], 'inheritance': 'X-linked Recessive', 'prevalence': '1 in 5,000 males', 'category': 'Rare Disease', 'origin': 'Germline'},
            'FMR1': {'diseases': ['Fragile X Syndrome'], 'inheritance': 'X-linked Dominant', 'prevalence': '1 in 4,000 males', 'category': 'Rare Disease', 'origin': 'Germline'},
            'GBA': {'diseases': ['Gaucher Disease'], 'inheritance': 'Autosomal Recessive', 'prevalence': '1 in 40,000', 'category': 'Rare Disease', 'origin': 'Germline'},
            'F8': {'diseases': ['Hemophilia A'], 'inheritance': 'X-linked Recessive', 'prevalence': '1 in 5,000 males', 'category': 'Rare Disease', 'origin': 'Germline'},
            'PAH': {'diseases': ['Phenylketonuria'], 'inheritance': 'Autosomal Recessive', 'prevalence': '1 in 10,000', 'category': 'Rare Disease', 'origin': 'Germline'},
            'SMN1': {'diseases': ['Spinal Muscular Atrophy'], 'inheritance': 'Autosomal Recessive', 'prevalence': '1 in 10,000', 'category': 'Rare Disease', 'origin': 'Germline'}
        }
    
    def annotate_variant(
        self,
        variant: Dict[str, Any],
        ml_prediction: Dict[str, Any],
        patient_ancestry: str = 'Unknown'
    ) -> Dict[str, Any]:
        """
        Comprehensive clinical annotation of variant
        
        Args:
            variant: Variant information dictionary
            ml_prediction: ML model prediction with classification and probability
            patient_ancestry: Patient ancestry for population-specific interpretation
            
        Returns:
            Complete clinical annotation dictionary
        """
        
        # Validate ML prediction input
        required_keys = {'classification', 'pathogenic_probability'}
        if not required_keys.issubset(ml_prediction.keys()):
            raise ValueError(f"ML prediction missing required keys: {required_keys - set(ml_prediction.keys())}")
        
        gene = variant.get('gene', 'Unknown')
        variant_id = variant.get('id')
        
        # Get population-specific frequency from gnomAD
        pop_freq = get_population_frequency(variant_id, patient_ancestry)
        
        # Determine ACMG criteria support
        acmg_criteria = self._determine_acmg_criteria(variant, ml_prediction, pop_freq)
        
        # Determine annotation confidence
        annotation_confidence = self._assess_annotation_confidence(ml_prediction, pop_freq, gene)
        
        # Get variant origin (germline vs somatic)
        variant_origin = self._get_variant_origin(gene)
        
        annotation = {
            'variant': variant,
            'ml_classification': ml_prediction,
            'pharmacogenomics': self._get_drug_recommendations(gene),
            'disease_association': self._get_disease_info(gene),
            'clinical_actionability': self._assess_actionability(variant, ml_prediction, pop_freq),
            'patient_impact': self._generate_patient_summary(gene, ml_prediction),
            'population_data': {
                'patient_ancestry': patient_ancestry,
                'allele_frequency_in_population': pop_freq,
                'gnomad_integrated': True
            },
            'acmg_support': acmg_criteria,
            'annotation_confidence': annotation_confidence,
            'variant_origin': variant_origin
        }
        
        return annotation
    
    def _determine_acmg_criteria(
        self,
        variant: Dict[str, Any],
        ml_prediction: Dict[str, Any],
        pop_freq: float
    ) -> List[str]:
        """Map to ACMG criteria codes"""
        criteria = []
        
        consequence = variant.get('consequence', '')
        classification = ml_prediction.get('classification', '')
        
        # Pathogenic criteria
        if consequence in ['frameshift_variant', 'nonsense_variant']:
            criteria.append('PVS1')  # Null variant in LoF gene
        
        if pop_freq and pop_freq < 0.0001:
            criteria.append('PM2')  # Absent/rare in population databases
        
        if classification in ['Pathogenic', 'Likely Pathogenic']:
            criteria.append('PP3')  # Computational evidence
        
        # Benign criteria
        if pop_freq and pop_freq > 0.05:
            criteria.append('BA1')  # High allele frequency
        
        if consequence == 'synonymous_variant':
            criteria.append('BP7')  # Synonymous with no splice impact
        
        return criteria
    
    def _assess_annotation_confidence(
        self,
        ml_prediction: Dict[str, Any],
        pop_freq: Optional[float],
        gene: str
    ) -> str:
        """Determine overall annotation confidence level"""
        
        ml_confidence = ml_prediction.get('confidence', 0)
        has_disease_data = gene in self.disease_associations
        has_pop_data = pop_freq is not None
        
        confidence_score = 0
        if ml_confidence > 0.9:
            confidence_score += 3
        elif ml_confidence > 0.7:
            confidence_score += 2
        else:
            confidence_score += 1
        
        if has_disease_data:
            confidence_score += 2
        if has_pop_data:
            confidence_score += 1
        
        if confidence_score >= 5:
            return "High"
        elif confidence_score >= 3:
            return "Moderate"
        else:
            return "Low"
    
    def _get_variant_origin(self, gene: str) -> str:
        """Determine if variant is typically germline or somatic"""
        disease_info = self.disease_associations.get(gene, {})
        return disease_info.get('origin', 'Unknown')
    
    def _get_drug_recommendations(self, gene: str) -> Dict[str, Any]:
        if gene in self.drug_gene_db:
            return self.drug_gene_db[gene]
        return {'drugs': [], 'indication': 'No specific therapies', 'evidence_level': 'N/A'}
    
    def _get_disease_info(self, gene: str) -> Dict[str, Any]:
        if gene in self.disease_associations:
            return self.disease_associations[gene]
        return {
            'diseases': ['Unknown'],
            'inheritance': 'Unknown',
            'prevalence': 'Unknown',
            'category': 'Unknown',
            'origin': 'Unknown'
        }
    
    def _assess_actionability(
        self,
        variant: Dict[str, Any],
        ml_prediction: Dict[str, Any],
        pop_freq: Optional[float]
    ) -> str:
        """
        Determine clinical actionability with population frequency consideration
        """
        classification = ml_prediction.get('classification', 'Uncertain Significance')
        gene = variant.get('gene', 'Unknown')
        
        # Check if variant is common in population (likely benign)
        if pop_freq and pop_freq > 0.01:
            return "LOW - Common population variant, likely benign"
        
        # High actionability genes (therapies available)
        actionable_genes = ['BRCA1', 'BRCA2', 'EGFR', 'KRAS', 'CFTR', 'HBB', 'F8', 'GBA', 'DMD', 'SMN1']
        
        if classification in ['Pathogenic', 'Likely Pathogenic']:
            if gene in actionable_genes:
                return "HIGH - Clinical action recommended (therapies available)"
            else:
                return "MODERATE - Genetic counseling recommended"
        elif classification == 'Uncertain Significance':
            return "LOW - Monitoring and periodic re-evaluation"
        else:
            return "MINIMAL - No immediate action required"
    
    def _generate_patient_summary(
        self,
        gene: str,
        ml_prediction: Dict[str, Any]
    ) -> str:
        classification = ml_prediction.get('classification', 'Uncertain')
        summaries = {
            'Pathogenic': f"Significant genetic change in {gene} gene increases health risks.",
            'Likely Pathogenic': f"Genetic change in {gene} likely affects health.",
            'Uncertain Significance': f"Genetic change in {gene} needs more research.",
            'Likely Benign': f"Genetic change in {gene} unlikely to affect health.",
            'Benign': f"Common variation in {gene} with no health concerns."
        }
        return summaries.get(classification, "Discuss with healthcare provider.")
    
    def generate_clinical_report(
        self,
        annotations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate comprehensive clinical report from annotations"""
        
        actionable = [
            a for a in annotations 
            if a['ml_classification']['classification'] in ['Pathogenic', 'Likely Pathogenic']
        ]
        
        # Categorize by disease type
        cancer_variants = [a for a in actionable if a['disease_association'].get('category') == 'Cancer Predisposition']
        rare_disease_variants = [a for a in actionable if a['disease_association'].get('category') == 'Rare Disease']
        oncology_variants = [a for a in actionable if a['disease_association'].get('category') == 'Oncology']
        
        return {
            'summary': {
                'total_variants': len(annotations),
                'pathogenic': len([a for a in annotations if 'Pathogenic' in a['ml_classification']['classification']]),
                'uncertain': len([a for a in annotations if 'Uncertain' in a['ml_classification']['classification']]),
                'benign': len([a for a in annotations if 'Benign' in a['ml_classification']['classification']])
            },
            'categorized_findings': {
                'cancer_predisposition': len(cancer_variants),
                'rare_diseases': len(rare_disease_variants),
                'oncology_somatic': len(oncology_variants)
            },
            'priority_variants': sorted(
                actionable,
                key=lambda x: x['ml_classification']['pathogenic_probability'],
                reverse=True
            )[:5],
            'genetic_counseling_indicated': len(actionable) > 0,
            'high_confidence_findings': len([a for a in actionable if a['annotation_confidence'] == 'High'])
        }


# ----------------------------------------------------------------------
# Unit Tests
# ----------------------------------------------------------------------
def run_validation_tests():
    """Test cases for robustness"""
    
    print("\n" + "="*70)
    print("RUNNING VALIDATION TESTS")
    print("="*70)
    
    annotator = ClinicalAnnotator()
    
    # Test 1: VUS + high population frequency
    print("\n[Test 1] VUS with high population frequency")
    test1_variant = {'id': 'chr7:55242464:G>A', 'gene': 'EGFR', 'consequence': 'missense_variant', 'allele_frequency': 0.05, 'quality': 55.0}
    test1_ml = {'classification': 'Uncertain Significance', 'pathogenic_probability': 0.45, 'confidence': 0.55}
    result1 = annotator.annotate_variant(test1_variant, test1_ml, 'East Asian')
    print(f"  Actionability: {result1['clinical_actionability']}")
    print(f"  Expected: LOW (common variant)")
    assert 'LOW' in result1['clinical_actionability'] or 'Common' in result1['clinical_actionability']
    print("  ✓ PASS")
    
    # Test 2: Pathogenic + non-actionable gene
    print("\n[Test 2] Pathogenic in non-actionable gene")
    test2_variant = {'id': 'chr1:12345:A>G', 'gene': 'UNKNOWN_GENE', 'consequence': 'frameshift_variant', 'allele_frequency': 0.0001, 'quality': 55.0}
    test2_ml = {'classification': 'Pathogenic', 'pathogenic_probability': 0.92, 'confidence': 0.92}
    result2 = annotator.annotate_variant(test2_variant, test2_ml, 'European')
    print(f"  Actionability: {result2['clinical_actionability']}")
    print(f"  Expected: MODERATE (no specific therapies)")
    assert 'MODERATE' in result2['clinical_actionability']
    print("  ✓ PASS")
    
    # Test 3: Benign + rare population
    print("\n[Test 3] Benign classification despite rare frequency")
    test3_variant = {'id': 'chr2:67890:C>T', 'gene': 'TP53', 'consequence': 'synonymous_variant', 'allele_frequency': 0.0001, 'quality': 55.0}
    test3_ml = {'classification': 'Benign', 'pathogenic_probability': 0.05, 'confidence': 0.95}
    result3 = annotator.annotate_variant(test3_variant, test3_ml, 'African American')
    print(f"  Classification: {result3['ml_classification']['classification']}")
    print(f"  ACMG Support: {result3['acmg_support']}")
    print(f"  Expected: Benign with BP7 (synonymous)")
    assert 'BP7' in result3['acmg_support']
    print("  ✓ PASS")
    
    print("\n" + "="*70)
    print("ALL VALIDATION TESTS PASSED ✓")
    print("="*70)


if __name__ == "__main__":
    # Run validation tests
    run_validation_tests()
    
    # Example annotation
    print("\n\nExample Annotation:")
    annotator = ClinicalAnnotator()
    
    test_variant = {
        'id': 'chr17:43044295:T>C',
        'gene': 'BRCA1',
        'consequence': 'missense_variant',
        'allele_frequency': 0.0001,
        'quality': 55.0
    }
    
    test_ml = {
        'variant_id': 'chr17:43044295:T>C',
        'classification': 'Likely Pathogenic',
        'pathogenic_probability': 0.82,
        'confidence': 0.82
    }
    
    annotation = annotator.annotate_variant(test_variant, test_ml, 'East Asian')
    print(json.dumps(annotation, indent=2))
