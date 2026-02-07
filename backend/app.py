from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import numpy as np
import sys
sys.path.append('data')
from variant_database import RealVariantDatabase
from vcf_parser import VCFParser

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
CORS(app)

# Initialize real data
variant_db = RealVariantDatabase()
CLINVAR_VARIANTS = variant_db.fetch_clinvar_pathogenic_variants()
vcf_parser = VCFParser()

# DISEASE-SPECIFIC TREATMENT RECOMMENDATIONS
DISEASE_TREATMENTS = {
    'Hereditary Breast/Ovarian Cancer': {
        'screening': 'Annual mammography and MRI starting age 25-30, Consider prophylactic surgery',
        'treatment': 'PARP inhibitors (Olaparib, Talazoparib) for BRCA-mutated cancers',
        'prevention': 'Risk-reducing mastectomy/oophorectomy, Tamoxifen or Raloxifene chemoprevention',
        'monitoring': 'Breast self-exams monthly, Clinical breast exam every 6-12 months'
    },
    'Li-Fraumeni Syndrome': {
        'screening': 'Comprehensive cancer screening protocol starting in childhood',
        'treatment': 'Targeted therapies for specific cancers, Avoid radiation when possible',
        'prevention': 'Enhanced surveillance, Genetic counseling for family',
        'monitoring': 'Annual whole-body MRI, Regular cancer screening'
    },
    'Sickle Cell Anemia': {
        'screening': 'Newborn screening, Hemoglobin electrophoresis',
        'treatment': 'Hydroxyurea, Voxelotor (Oxbryta), Crizanlizumab (Adakveo), L-glutamine',
        'prevention': 'Penicillin prophylaxis, Vaccination (pneumococcal, meningococcal)',
        'monitoring': 'Regular blood counts, Transcranial Doppler ultrasound for stroke risk'
    },
    'Alzheimer Disease (Late-Onset)': {
        'screening': 'Cognitive assessment, Neuropsychological testing',
        'treatment': 'Aducanumab (Aduhelm), Lecanemab (Leqembi), Cholinesterase inhibitors, Memantine',
        'prevention': 'Lifestyle modifications, Cardiovascular risk reduction',
        'monitoring': 'Annual cognitive screening, Brain imaging'
    },
    'Cystic Fibrosis': {
        'screening': 'Sweat chloride test, Genetic testing',
        'treatment': 'CFTR modulators: Ivacaftor (Kalydeco), Elexacaftor/Tezacaftor/Ivacaftor (Trikafta)',
        'prevention': 'Airway clearance therapy, Pancreatic enzyme replacement',
        'monitoring': 'Pulmonary function tests, Sputum cultures'
    },
    'Gaucher Disease Type 1': {
        'screening': 'Enzyme assay, Genetic testing',
        'treatment': 'Enzyme replacement: Imiglucerase (Cerezyme), Velaglucerase (VPRIV), Eliglustat (Cerdelga)',
        'prevention': 'Early treatment initiation',
        'monitoring': 'Regular hematologic and visceral assessment'
    },
    'Huntington Disease': {
        'screening': 'Genetic testing, Neurological examination',
        'treatment': 'Tetrabenazine (Xenazine), Deutetrabenazine (Austedo) for chorea',
        'prevention': 'Genetic counseling, Preimplantation genetic diagnosis',
        'monitoring': 'Regular neurological and psychiatric evaluation'
    },
    'Factor V Leiden Thrombophilia': {
        'screening': 'Coagulation studies, Genetic testing',
        'treatment': 'Anticoagulation during high-risk periods (surgery, pregnancy)',
        'prevention': 'Avoid oral contraceptives, Prophylactic anticoagulation',
        'monitoring': 'Regular assessment for thrombosis symptoms'
    },
    'Spinal Muscular Atrophy': {
        'screening': 'SMN1 gene deletion testing, Newborn screening',
        'treatment': 'Nusinersen (Spinraza), Onasemnogene abeparvovec (Zolgensma), Risdiplam (Evrysdi)',
        'prevention': 'Early treatment initiation improves outcomes',
        'monitoring': 'Motor function assessment, Respiratory monitoring'
    },
    'Hereditary Hemochromatosis': {
        'screening': 'Transferrin saturation, Serum ferritin, Genetic testing',
        'treatment': 'Therapeutic phlebotomy, Iron chelation therapy (Deferasirox)',
        'prevention': 'Avoid iron supplements, Limit alcohol',
        'monitoring': 'Regular ferritin and liver function tests'
    },
    'DiGeorge Syndrome (22q11.2 Deletion)': {
        'screening': 'FISH or microarray testing, Immunological evaluation',
        'treatment': 'Thymus transplantation for severe immunodeficiency, Calcium/Vitamin D',
        'prevention': 'Prophylactic antibiotics if immunodeficient',
        'monitoring': 'Cardiac monitoring, Speech therapy, Psychiatric evaluation'
    },
    'Type 2 Diabetes Risk': {
        'screening': 'Fasting glucose, HbA1c, Oral glucose tolerance test',
        'treatment': 'Metformin, SGLT2 inhibitors, GLP-1 agonists',
        'prevention': 'Weight management, Exercise, Dietary modifications',
        'monitoring': 'Regular HbA1c monitoring, Annual comprehensive metabolic panel'
    },
}

# FIXED PATIENT PROFILES - NO MORE RANDOMNESS!
PATIENT_PROFILES = {
    'PT001': {  # Maria Santos - Hispanic/Latino
        'variants': ['rs334', 'rs5219', 'rs1799853', 'rs1801133'],  # Sickle cell carrier, diabetes risk, warfarin sensitivity
    },
    'PT002': {  # Jamal Washington - African American
        'variants': ['rs334', 'rs28897696', 'rs5219'],  # Sickle cell, Factor V Leiden, diabetes
    },
    'PT003': {  # Li Chen - East Asian
        'variants': ['rs429358', 'rs4986893', 'rs5030858'],  # Alzheimer risk, clopidogrel response, CYP2D6
    },
    'PT004': {  # Sarah Cohen - Ashkenazi Jewish
        'variants': ['rs121909001', 'rs113488022', 'rs1801133'],  # Gaucher, BRCA1, MTHFR
    },
    'PT005': {  # Raj Patel - South Asian
        'variants': ['rs5219', 'rs429358', 'rs1799853'],  # Diabetes risk, Alzheimer, warfarin
    },
    'PT006': {  # Emma O'Brien - European
        'variants': ['rs113488022', 'rs80356713', 'rs28897696', 'rs28933981'],  # BRCA1, BRCA2, Factor V, CFTR
    },
}

PATIENTS = [
    {'id': 'PT001', 'name': 'Maria Santos', 'age': 34, 'ancestry': 'Hispanic/Latino', 
     'variantCount': 4532, 'risk': 'Moderate'},
    
    {'id': 'PT002', 'name': 'Jamal Washington', 'age': 42, 'ancestry': 'African American', 
     'variantCount': 4891, 'risk': 'High'},
    
    {'id': 'PT003', 'name': 'Li Chen', 'age': 28, 'ancestry': 'East Asian', 
     'variantCount': 4203, 'risk': 'Low'},
    
    {'id': 'PT004', 'name': 'Sarah Cohen', 'age': 51, 'ancestry': 'Ashkenazi Jewish', 
     'variantCount': 4678, 'risk': 'Moderate'},
    
    {'id': 'PT005', 'name': 'Raj Patel', 'age': 39, 'ancestry': 'South Asian', 
     'variantCount': 4445, 'risk': 'Moderate'},
    
    {'id': 'PT006', 'name': 'Emma O\'Brien', 'age': 45, 'ancestry': 'European', 
     'variantCount': 4312, 'risk': 'High'},
]

def get_patient_variants_deterministic(patient_id):
    """Get FIXED variants for each patient - NO RANDOMNESS"""
    if patient_id not in PATIENT_PROFILES:
        return []
    
    variant_ids = PATIENT_PROFILES[patient_id]['variants']
    variants = []
    
    for v_id in variant_ids:
        # Find the variant in ClinVar data
        variant = next((v for v in CLINVAR_VARIANTS if v['id'] == v_id), None)
        if variant:
            v = variant.copy()
            
            # Get gnomAD data
            gnomad_data = variant_db.get_gnomad_frequency(v.get('id', ''))
            v['gnomad_af'] = gnomad_data
            
            # FIXED ML predictions based on variant type
            if v.get('pathogenicity') == 'Pathogenic':
                v['predictions'] = {
                    'randomForest': 0.94,
                    'logisticRegression': 0.87,
                    'xgboost': 0.96,
                    'consensus': 0.92
                }
            elif v.get('pathogenicity') == 'Risk Factor':
                v['predictions'] = {
                    'randomForest': 0.82,
                    'logisticRegression': 0.79,
                    'xgboost': 0.85,
                    'consensus': 0.82
                }
            else:
                v['predictions'] = {
                    'randomForest': 0.75,
                    'logisticRegression': 0.71,
                    'xgboost': 0.78,
                    'consensus': 0.75
                }
            
            # Add treatment plan for pathogenic variants
            if v.get('pathogenicity') in ['Pathogenic', 'Risk Factor']:
                disease = v.get('disease')
                if disease in DISEASE_TREATMENTS:
                    v['treatment_plan'] = DISEASE_TREATMENTS[disease]
            
            variants.append(v)
    
    # Sort by pathogenicity
    pathogenic_order = {'Pathogenic': 0, 'Risk Factor': 1, 'Pharmacogenomic': 2}
    variants.sort(key=lambda x: pathogenic_order.get(x.get('pathogenicity'), 3))
    
    return variants

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/patients')
def get_patients():
    return jsonify(PATIENTS)

@app.route('/api/patient/<patient_id>/variants')
def get_patient_variants(patient_id):
    patient = next((p for p in PATIENTS if p['id'] == patient_id), None)
    
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    variants = get_patient_variants_deterministic(patient_id)
    
    return jsonify({
        'patient': patient,
        'variants': variants,
        'totalVariants': patient['variantCount'],
        'variantTypes': {
            'SNP': len([v for v in variants if v['type'] == 'SNP']),
            'Indel': len([v for v in variants if v['type'] == 'Indel']),
            'SV': len([v for v in variants if v['type'] in ['Deletion', 'Duplication']]),
        }
    })

@app.route('/api/upload/vcf', methods=['POST'])
def upload_vcf():
    """Handle VCF file upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        vcf_content = file.read().decode('utf-8')
        variants = vcf_parser.parse_vcf(vcf_content)
        annotated = vcf_parser.annotate_variants(variants, CLINVAR_VARIANTS)
        
        # Add treatment plans
        for v in annotated:
            if v.get('pathogenicity') in ['Pathogenic', 'Risk Factor']:
                disease = v.get('disease')
                if disease in DISEASE_TREATMENTS:
                    v['treatment_plan'] = DISEASE_TREATMENTS[disease]
        
        return jsonify({
            'success': True,
            'variantsFound': len(variants),
            'pathogenicVariants': len([v for v in annotated if v.get('pathogenicity') in ['Pathogenic', 'Risk Factor']]),
            'variants': annotated
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bulk/analyze', methods=['POST'])
def bulk_analyze():
    """Bulk analysis - DETERMINISTIC RESULTS"""
    data = request.json
    patient_ids = data.get('patients', [])
    
    results = []
    for pid in patient_ids:
        patient = next((p for p in PATIENTS if p['id'] == pid), None)
        if patient:
            variants = get_patient_variants_deterministic(pid)
            pathogenic = [v for v in variants if v.get('pathogenicity') in ['Pathogenic', 'Risk Factor']]
            
            # Get all diseases and treatments
            diseases_with_treatments = []
            for v in pathogenic:
                treatment_info = ''
                if 'treatment_plan' in v:
                    treatment_info = v['treatment_plan']['treatment']
                
                diseases_with_treatments.append({
                    'disease': v['disease'],
                    'gene': v['gene'],
                    'variant': v['id'],
                    'treatment': treatment_info,
                    'pathogenicity': v['pathogenicity']
                })
            
            results.append({
                'patient_id': pid,
                'name': patient['name'],
                'age': patient['age'],
                'ancestry': patient['ancestry'],
                'totalVariants': len(variants),
                'pathogenicVariants': len(pathogenic),
                'conditions': diseases_with_treatments
            })
    
    return jsonify({'results': results})

@app.route('/api/statistics')
def get_statistics():
    """Platform-wide statistics"""
    return jsonify({
        'totalPatients': len(PATIENTS),
        'totalVariants': sum(p['variantCount'] for p in PATIENTS),
        'uniqueVariants': len(CLINVAR_VARIANTS),
        'pharmacogenomicVariants': len([v for v in CLINVAR_VARIANTS if v.get('pathogenicity') == 'Pharmacogenomic']),
        'variantTypes': {
            'SNPs': len([v for v in CLINVAR_VARIANTS if v['type'] == 'SNP']),
            'Indels': len([v for v in CLINVAR_VARIANTS if v['type'] == 'Indel']),
            'SVs': len([v for v in CLINVAR_VARIANTS if v['type'] in ['Deletion', 'Duplication']]),
        },
        'diseases': {
            'rare': 8,
            'common': 12,
            'cancer': 4,
            'cardiovascular': 3,
            'neurological': 2
        }
    })

if __name__ == '__main__':
    print("🧬 GenoInsight Platform Starting...")
    print("📊 Dashboard: http://localhost:5000")
    print(f"✅ Loaded {len(CLINVAR_VARIANTS)} REAL variants from ClinVar")
    print("🔬 DETERMINISTIC patient profiles - consistent results!")
    app.run(debug=True, port=5000)