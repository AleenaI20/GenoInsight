import os
import pickle
import pandas as pd
import numpy as np
import vcfpy
from flask import Flask, request, jsonify

# -------------------------------
# Paths
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "../models")

# -------------------------------
# Load ML models
# -------------------------------
try:
    with open(os.path.join(MODEL_DIR, "rf_model.pkl"), "rb") as f:
        rf_model = pickle.load(f)
    with open(os.path.join(MODEL_DIR, "xgb_model.pkl"), "rb") as f:
        xgb_model = pickle.load(f)
except Exception as e:
    raise RuntimeError(f"Error loading models: {e}")

# -------------------------------
# Initialize Flask
# -------------------------------
app = Flask(__name__)

# -------------------------------
# Helper: parse VCF to DataFrame
# -------------------------------
def vcf_to_dataframe(vcf_path):
    """
    Reads a VCF file and converts it to a pandas DataFrame.
    Extracts basic info (CHROM, POS, REF, ALT, QUAL) and INFO fields.
    """
    reader = vcfpy.Reader.from_path(vcf_path)
    records = []

    for record in reader:
        rec_dict = {
            "CHROM": record.CHROM,
            "POS": record.POS,
            "REF": record.REF,
            "ALT": ",".join([str(a) for a in record.ALT]),
            "QUAL": record.QUAL,
        }
        for key, value in record.INFO.items():
            rec_dict[key] = value
        records.append(rec_dict)

    df = pd.DataFrame(records)
    return df

# -------------------------------
# Helper: feature extraction for ML
# -------------------------------
def prepare_features(df):
    """
    Convert VCF DataFrame to features expected by your ML models.
    Adjust according to your trained model features.
    """
    df_features = pd.DataFrame()
    df_features["REF_len"] = df["REF"].apply(len)
    df_features["ALT_len"] = df["ALT"].apply(lambda x: max([len(a) for a in x.split(",")]))
    df_features["QUAL"] = df["QUAL"].fillna(0)
    return df_features

# -------------------------------
# Flask routes
# -------------------------------
@app.route("/")
def index():
    return "GenoInsight API is running. Use POST /predict with VCF file."

@app.route("/predict", methods=["POST"])
def predict():
    if "vcf" not in request.files:
        return jsonify({"error": "No VCF file provided"}), 400
    
    vcf_file = request.files["vcf"]
    vcf_path = os.path.join(BASE_DIR, "temp.vcf")
    vcf_file.save(vcf_path)
    
    try:
        df_vcf = vcf_to_dataframe(vcf_path)
        features = prepare_features(df_vcf)
        
        # Predictions
        rf_preds = rf_model.predict(features)
        xgb_preds = xgb_model.predict(features)
        
        # Combine predictions with original variants
        df_vcf["RF_Pred"] = rf_preds
        df_vcf["XGB_Pred"] = xgb_preds

        results = df_vcf.to_dict(orient="records")
        return jsonify({"predictions": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(vcf_path):
            os.remove(vcf_path)

# -------------------------------
# Run Flask
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
