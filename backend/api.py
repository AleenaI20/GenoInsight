"""
Flask API for GenoInsight Platform
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import sys
from werkzeug.utils import secure_filename

sys.path.insert(0, os.path.dirname(__file__))

from variant_parser import VariantParser
from ml_classifier import VariantPathogenicityClassifier
from clinical_annotator import ClinicalAnnotator

app = Flask(__name__)

# FIX CORS - Allow all origins for ngrok
CORS(app, resources={r"/*": {"origins": "*"}})

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'vcf', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ml_classifier = VariantPathogenicityClassifier()
clinical_annotator = ClinicalAnnotator()

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'GenoInsight API',
        'version': '1.0.0'
    }), 200


@app.route('/api/upload-vcf', methods=['POST'])
def upload_vcf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            parser = VariantParser(filepath)
            variants = parser.parse_vcf()
            filtered_variants = parser.filter_variants()
            
            return jsonify({
                'success': True,
                'total_variants': len(variants),
                'filtered_variants': len(filtered_variants),
                'variants': filtered_variants[:50]
            }), 200
            
        except Exception as e:
            return jsonify({'error': f'Error parsing VCF: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400


@app.route('/api/analyze-variant', methods=['POST'])
def analyze_variant():
    data = request.get_json()
    
    if not data or 'variant' not in data:
        return jsonify({'error': 'No variant data provided'}), 400
    
    variant = data['variant']
    
    try:
        ml_prediction = ml_classifier.predict_pathogenicity(variant)
        annotation = clinical_annotator.annotate_variant(variant, ml_prediction)
        
        return jsonify({
            'success': True,
            'analysis': annotation
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@app.route('/api/analyze-batch', methods=['POST'])
def analyze_batch():
    data = request.get_json()
    
    if not data or 'variants' not in data:
        return jsonify({'error': 'No variants provided'}), 400
    
    variants = data['variants']
    
    try:
        annotations = []
        
        for variant in variants:
            ml_prediction = ml_classifier.predict_pathogenicity(variant)
            annotation = clinical_annotator.annotate_variant(variant, ml_prediction)
            annotations.append(annotation)
        
        clinical_report = clinical_annotator.generate_clinical_report(annotations)
        
        return jsonify({
            'success': True,
            'total_analyzed': len(annotations),
            'annotations': annotations,
            'clinical_report': clinical_report
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@app.route('/api/sample-data', methods=['GET'])
def get_sample_data():
    sample_variants = [
        {'id': 'chr1:12345:A>G', 'gene': 'BRCA1', 'consequence': 'missense_variant', 'allele_frequency': 0.0001, 'quality': 50.0},
        {'id': 'chr2:67890:C>T', 'gene': 'TP53', 'consequence': 'nonsense_variant', 'allele_frequency': 0.0002, 'quality': 45.0},
        {'id': 'chr7:55242464:G>A', 'gene': 'EGFR', 'consequence': 'missense_variant', 'allele_frequency': 0.001, 'quality': 60.0},
        {'id': 'chr17:43044295:T>C', 'gene': 'BRCA1', 'consequence': 'splice_site_variant', 'allele_frequency': 0.0003, 'quality': 55.0},
        {'id': 'chr13:32315474:G>T', 'gene': 'BRCA2', 'consequence': 'frameshift_variant', 'allele_frequency': 0.0001, 'quality': 48.0},
        {'id': 'chr12:25398285:C>G', 'gene': 'KRAS', 'consequence': 'missense_variant', 'allele_frequency': 0.0005, 'quality': 52.0},
        {'id': 'chr10:89624227:T>A', 'gene': 'PTEN', 'consequence': 'frameshift_variant', 'allele_frequency': 0.0002, 'quality': 58.0},
        {'id': 'chr11:108175438:G>C', 'gene': 'ATM', 'consequence': 'splice_site_variant', 'allele_frequency': 0.0004, 'quality': 47.0},
        {'id': 'chr3:37050300:A>T', 'gene': 'MLH1', 'consequence': 'nonsense_variant', 'allele_frequency': 0.0001, 'quality': 53.0},
        {'id': 'chr2:47641559:C>A', 'gene': 'MSH2', 'consequence': 'missense_variant', 'allele_frequency': 0.0003, 'quality': 49.0},
        {'id': 'chr5:112162856:G>T', 'gene': 'APC', 'consequence': 'frameshift_variant', 'allele_frequency': 0.0002, 'quality': 56.0},
        {'id': 'chr9:21971120:T>G', 'gene': 'CDKN2A', 'consequence': 'missense_variant', 'allele_frequency': 0.0006, 'quality': 51.0},
        {'id': 'chr14:105246494:A>C', 'gene': 'AKT1', 'consequence': 'missense_variant', 'allele_frequency': 0.0004, 'quality': 54.0},
        {'id': 'chr19:1220571:G>A', 'gene': 'STK11', 'consequence': 'nonsense_variant', 'allele_frequency': 0.0001, 'quality': 48.0},
        {'id': 'chr6:117640000:C>T', 'gene': 'ROS1', 'consequence': 'splice_site_variant', 'allele_frequency': 0.0003, 'quality': 57.0},
        {'id': 'chr4:55141055:A>G', 'gene': 'PDGFRA', 'consequence': 'missense_variant', 'allele_frequency': 0.0007, 'quality': 46.0},
        {'id': 'chr15:90088702:G>A', 'gene': 'IDH2', 'consequence': 'missense_variant', 'allele_frequency': 0.0002, 'quality': 59.0},
        {'id': 'chr1:115256529:T>C', 'gene': 'NRAS', 'consequence': 'missense_variant', 'allele_frequency': 0.0004, 'quality': 50.0},
        {'id': 'chr17:7577548:C>T', 'gene': 'TP53', 'consequence': 'missense_variant', 'allele_frequency': 0.0001, 'quality': 55.0},
        {'id': 'chr13:32912299:A>G', 'gene': 'BRCA2', 'consequence': 'missense_variant', 'allele_frequency': 0.0002, 'quality': 52.0}
    ]
    
    return jsonify({
        'success': True,
        'sample_variants': sample_variants
    }), 200


if __name__ == '__main__':
    print("Initializing ML model...")
    
    try:
        ml_classifier.load_model()
        print("Model loaded!")
    except:
        ml_classifier.train_model()
        ml_classifier.save_model()
        print("Model trained!")
    
    print("Starting API...")
    app.run(debug=True, host='0.0.0.0', port=5000)
