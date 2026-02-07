import os
import pickle
import pandas as pd
import vcfpy
from flask import Flask, request, jsonify

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "../models")

with open(os.path.join(MODEL_DIR, "rf_model.pkl"), "rb") as f:
    rf_model = pickle.load(f)

with open(os.path.join(MODEL_DIR, "lr_model.pkl"), "rb") as f:
    lr_model = pickle.load(f)

with open(os.path.join(MODEL_DIR, "xgb_model.pkl"), "rb") as f:
    xgb_model = pickle.load(f)

app = Flask(__name__)

def vcf_to_df(vcf_path):
    reader = vcfpy.Reader.from_path(vcf_path)
    rows = []

    for rec in reader:
        info = rec.INFO
        rows.append({
            "REF_len": len(rec.REF),
            "ALT_len": max(len(str(a)) for a in rec.ALT),
            "QUAL": rec.QUAL or 0,
            "AF_EUR": info.get("AF_EUR", 0),
            "AF_AFR": info.get("AF_AFR", 0),
            "AF_EAS": info.get("AF_EAS", 0),
            "CHROM": rec.CHROM,
            "POS": rec.POS,
            "REF": rec.REF,
            "ALT": ",".join(map(str, rec.ALT))
        })

    return pd.DataFrame(rows)

@app.route("/")
def index():
    return "GenoInsight API running"

@app.route("/predict", methods=["POST"])
def predict():
    if "vcf" not in request.files:
        return jsonify({"error": "VCF file required"}), 400

    path = os.path.join(BASE_DIR, "temp.vcf")
    request.files["vcf"].save(path)

    try:
        df = vcf_to_df(path)
        X = df[["REF_len","ALT_len","QUAL","AF_EUR","AF_AFR","AF_EAS"]]

        df["RF_Pathogenic"] = rf_model.predict(X)
        df["LR_Pathogenic"] = lr_model.predict(X)
        df["XGB_Pathogenic"] = xgb_model.predict(X)

        return jsonify(df.to_dict(orient="records"))

    finally:
        os.remove(path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
