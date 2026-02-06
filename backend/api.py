"""
Flask API for GenoInsight Platform
---------------------------------
AI-powered genomic variant interpretation using ensemble ML models.

DISCLAIMER:
This system is for research and educational purposes only.
Not intended for clinical diagnosis or treatment decisions.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import sys

# Local imports
sys.path.insert(0, os.path.dirname(__file__))

from variant_parser import VariantParser
from ensemble_models import EnsembleVariantClassifier
from clinical_annotator import ClinicalAnnotator


# ---------------------------------------------------------------------
# App Configuration
# ---------------------------------------------------------------------
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"vcf", "txt"}
MAX_BATCH_SIZE = 1000  # safety limit

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------------------------------------------------------------
# Initialize Models
# ---------------------------------------------------------------------
ensemble_classifier = EnsembleVariantClassifier()
clinical_annotator = ClinicalAnnotator()


# ---------------------------------------------------------------------
# Utility Functions
# ---------------------------------------------------------------------
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_variant_payload(variant: dict) -> bool:
    required_keys = {"id", "gene", "consequence"}
    return isinstance(variant, dict) and required_keys.issubset(variant.keys())


# ---------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------
@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "GenoInsight API",
        "version": "2.0.1",
        "models": ["random_forest", "logistic_regression", "xgboost"],
        "ensemble_ready": ensemble_classifier.is_trained
    }), 200


# ---------------------------------------------------------------------
# VCF Upload & Parsing
# ---------------------------------------------------------------------
@app.route("/api/upload-vcf", methods=["POST"])
def upload_vcf():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    try:
        parser = VariantParser(filepath)
        variants = parser.parse_vcf()
        filtered_variants = parser.filter_variants()

        return jsonify({
            "success": True,
            "total_variants": len(variants),
            "filtered_variants": len(filtered_variants),
            "preview": filtered_variants[:50]
        }), 200

    except Exception as e:
        return jsonify({"error": f"VCF parsing failed: {str(e)}"}), 500


# ---------------------------------------------------------------------
# Single Variant Analysis
# ---------------------------------------------------------------------
@app.route("/api/analyze-variant", methods=["POST"])
def analyze_variant():
    data = request.get_json()

    if not data or "variant" not in data:
        return jsonify({"error": "No variant data provided"}), 400

    variant = data["variant"]
    use_ensemble = bool(data.get("use_ensemble", True))

    if not validate_variant_payload(variant):
        return jsonify({"error": "Invalid variant format"}), 400

    try:
        prediction = ensemble_classifier.predict_pathogenicity(
            variant, use_ensemble=use_ensemble
        )

        annotation = clinical_annotator.annotate_variant(
            variant, prediction
        )

        return jsonify({
            "success": True,
            "analysis": annotation,
            "model_mode": "ensemble" if use_ensemble else "single"
        }), 200

    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


# ---------------------------------------------------------------------
# Batch Variant Analysis
# ---------------------------------------------------------------------
@app.route("/api/analyze-batch", methods=["POST"])
def analyze_batch():
    data = request.get_json()

    if not data or "variants" not in data:
        return jsonify({"error": "No variants provided"}), 400

    variants = data["variants"]
    use_ensemble = bool(data.get("use_ensemble", True))

    if not isinstance(variants, list):
        return jsonify({"error": "Variants must be a list"}), 400

    if len(variants) > MAX_BATCH_SIZE:
        return jsonify({"error": f"Batch size exceeds {MAX_BATCH_SIZE} variants"}), 400

    try:
        annotations = []

        for variant in variants:
            if not validate_variant_payload(variant):
                continue

            prediction = ensemble_classifier.predict_pathogenicity(
                variant, use_ensemble=use_ensemble
            )

            annotation = clinical_annotator.annotate_variant(
                variant, prediction
            )
            annotations.append(annotation)

        report = clinical_annotator.generate_clinical_report(annotations)

        return jsonify({
            "success": True,
            "total_analyzed": len(annotations),
            "annotations": annotations,
            "clinical_report": report,
            "model_mode": "ensemble" if use_ensemble else "single"
        }), 200

    except Exception as e:
        return jsonify({"error": f"Batch analysis failed: {str(e)}"}), 500


# ---------------------------------------------------------------------
# Sample Data Endpoint
# ---------------------------------------------------------------------
@app.route("/api/sample-data", methods=["GET"])
def get_sample_data():
    return jsonify({
        "success": True,
        "sample_variants": [
            {
                "id": "chr17:43044295:T>C",
                "gene": "BRCA1",
                "consequence": "missense_variant",
                "cohort_allele_frequency": 0.0003,
                "quality": 55.0
            },
            {
                "id": "chr7:55242464:G>A",
                "gene": "EGFR",
                "consequence": "missense_variant",
                "cohort_allele_frequency": 0.001,
                "quality": 60.0
            }
        ]
    }), 200


# ---------------------------------------------------------------------
# Model Metadata
# ---------------------------------------------------------------------
@app.route("/api/model-info", methods=["GET"])
def model_info():
    return jsonify({
        "available_models": {
            "random_forest": "Primary production model (explainable)",
            "logistic_regression": "Baseline interpretable model",
            "xgboost": "High-performance benchmark model"
        },
        "default_model": "random_forest",
        "ensemble_strategy": "Mean probability aggregation",
        "metrics": ensemble_classifier.metrics
    }), 200


# ---------------------------------------------------------------------
# App Startup
# ---------------------------------------------------------------------
if __name__ == "__main__":
    print("Initializing GenoInsight Ensemble Models...")

    ensemble_classifier.train_all_models()

    print("✓ All models trained successfully")
    print("Starting GenoInsight API v2.0.1")
    app.run(host="0.0.0.0", port=5000, debug=True)

