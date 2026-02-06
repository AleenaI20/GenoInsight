import os
import pandas as pd
import pickle
import vcf
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

clinvar_vcf = 'data/clinvar.vcf.gz'
gnomad_vcf_files = [f'data/gnomad_chr{i}.vcf.bgz' for i in range(1,23)]
pharma_genes = ['CYP2D6', 'CYP2C19']

def extract_features(vcf_path):
    vcf_reader = vcf.Reader(filename=vcf_path)
    data = []
    for record in vcf_reader:
        data.append({
            'consequence': len(record.ALT),
            'allele_freq': record.INFO.get('AF',[0])[0],
            'is_pharma_gene': int(record.INFO.get('GENE','') in pharma_genes),
            'quality': record.QUAL,
            'coding': int('CDS' in record.INFO.get('FUNCTION',''))
        })
    return pd.DataFrame(data)

def train_models():
    df = extract_features(clinvar_vcf)
    df['label'] = [1]*len(df)
    X = df[['consequence','allele_freq','is_pharma_gene','quality','coding']]
    y = df['label']

    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X,y)
    pickle.dump(rf, open('models/rf_model.pkl','wb'))

    lr = LogisticRegression()
    lr.fit(X,y)
    pickle.dump(lr, open('models/lr_model.pkl','wb'))

    xgb = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    xgb.fit(X,y)
    pickle.dump(xgb, open('models/xgb_model.pkl','wb'))

train_models()

@app.route('/upload', methods=['POST'])
def upload_vcf():
    file = request.files['file']
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    df = extract_features(filepath)
    rf = pickle.load(open('models/rf_model.pkl','rb'))
    df['rf_pred'] = rf.predict(df[['consequence','allele_freq','is_pharma_gene','quality','coding']])
    return df.to_json(orient='records')

if __name__ == '__main__':
    app.run(debug=True)
