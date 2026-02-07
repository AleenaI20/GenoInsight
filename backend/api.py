import os
import pickle
import pandas as pd
import numpy as np
import vcfpy
from flask import Flask, request, render_template_string
import plotly.express as px
import plotly.io as pio

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
# VCF parser
# -------------------------------
def vcf_to_dataframe(vcf_path):
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
    return pd.DataFrame(records)

# -------------------------------
# Feature preparation
# -------------------------------
def prepare_features(df):
    df_features = pd.DataFrame()
    df_features["REF_len"] = df["REF"].apply(len)
    df_features["ALT_len"] = df["ALT"].apply(lambda x: max([len(a) for a in x.split(",")]))
    df_features["QUAL"] = df["QUAL"].fillna(0)
    return df_features

# -------------------------------
# Dashboard HTML template
# -------------------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>GenoInsight Dashboard</title>
</head>
<body>
    <h1>GenoInsight Dashboard</h1>
    <form action="/dashboard" method="post" enctype="multipart/form-data">
        <label>Upload VCF File:</label>
        <input type="file" name="vcf" required>
        <input type="submit" value="Predict">
    </form>

    {% if predictions %}
        <h2>Predictions Table</h2>
        <table border="1" cellpadding="5">
            <tr>
            {% for col in predictions.columns %}
                <th>{{col}}</th>
            {% endfor %}
            </tr>
            {% for row in predictions.values %}
            <tr>
                {% for item in row %}
                    <td>{{item}}</td>
                {% endfor %}
            </tr>
            {% endfor %}
        </table>

        <h2>Plot: REF vs ALT Length</h2>
        {{plot_div|safe}}
    {% endif %}
</body>
</html>
"""

# -------------------------------
# Flask routes
# -------------------------------
@app.route("/")
def index():
    return "<h2>GenoInsight API Running. Go to /dashboard for predictions.</h2>"

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    predictions = None
    plot_div = ""
    if request.method == "POST":
        if "vcf" not in request.files:
            return "No VCF file uploaded", 400
        vcf_file = request.files["vcf"]
        vcf_path = os.path.join(BASE_DIR, "temp.vcf")
        vcf_file.save(vcf_path)
        try:
            df_vcf = vcf_to_dataframe(vcf_path)
            features = prepare_features(df_vcf)
            df_vcf["RF_Pred"] = rf_model.predict(features)
            df_vcf["XGB_Pred"] = xgb_model.predict(features)
            predictions = df_vcf

            # Plot using Plotly
            fig = px.scatter(df_vcf, x="REF_len", y="ALT_len", color="RF_Pred", hover_data=["CHROM","POS"])
            plot_div = pio.to_html(fig, full_html=False)
        finally:
            if os.path.exists(vcf_path):
                os.remove(vcf_path)

    return render_template_string(HTML_TEMPLATE, predictions=predictions, plot_div=plot_div)

# -------------------------------
# Run Flask
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
