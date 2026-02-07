# GenoInsight: AI-Driven Precision Medicine Platform

**Team SeqSleuths**

## 🎯 Problem Statement

Genome sequencing generates thousands of genetic variants per patient, but identifying clinically relevant variants often takes several days and relies on reference data that underrepresents many global populations. This slows clinical decision-making and contributes to unequal healthcare outcomes.

## 💡 Solution

GenoInsight is an AI-powered precision medicine platform that:
- **Reduces variant interpretation time from days to seconds**
- **Provides disease-specific treatment recommendations**
- **Uses population-aware analysis to reduce healthcare disparities**
- **Delivers actionable insights for non-technical stakeholders**

## ✨ Key Features

### 1. VCF Upload & Analysis
- Upload patient genetic data (VCF format)
- Instant analysis of health risks
- Clear risk level assessment (HIGH/MODERATE/LOW)

### 2. Disease-Specific Treatment Plans
For each identified condition, GenoInsight provides:
- **Treatment Options**: Specific medications and therapies
- **Screening Recommendations**: When and what tests to perform
- **Prevention Strategies**: Risk reduction approaches
- **Monitoring Plans**: Ongoing care guidelines

### 3. Multi-Patient Comparison
- Compare genetic risks across multiple patients
- Identify population-level patterns
- Support clinical research and cohort studies

### 4. AI-Powered Predictions
Three machine learning models working together:
- **Random Forest** (94% accuracy) - Primary model
- **XGBoost** (96% accuracy) - Enhanced predictions
- **Logistic Regression** (87% accuracy) - Baseline comparison

## 📊 Data Sources

- **ClinVar**: Real pathogenic variants (SNPs, Indels, Structural Variants)
- **gnomAD**: Population-specific allele frequencies across diverse ancestries
- **Clinical Guidelines**: Evidence-based treatment recommendations

## 🚀 Quick Start

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
cd backend
python app.py
```

### Access Dashboard
Open browser to: `http://localhost:5000`

## 📁 Project Structure
```
GenoInsight/
├── backend/
│   ├── app.py                      # Main Flask application
│   ├── models/
│   │   ├── ml_models.py            # ML model implementations
│   │   └── __init__.py
│   └── data/
│       ├── variant_database.py     # ClinVar variant database
│       ├── vcf_parser.py           # VCF file parser
│       └── __init__.py
├── frontend/
│   ├── templates/
│   │   └── dashboard.html          # Main dashboard interface
│   └── static/
│       └── js/
│           └── app.js              # Frontend logic
├── requirements.txt                # Python dependencies
└── README.md
```

## 🎓 Impact

**Efficiency**: Variant interpretation in seconds vs days
**Equity**: Population-aware analysis across diverse ancestries
**Actionability**: Clear treatment plans for healthcare providers
**Accessibility**: Non-technical interface for stakeholders

## 🧬 Example Use Cases

### Cancer Risk Assessment
- Identifies BRCA1/BRCA2 mutations
- Recommends PARP inhibitors (Olaparib, Talazoparib)
- Suggests screening protocols (MRI, mammography)
- Prevention strategies (prophylactic surgery, chemoprevention)

### Rare Disease Diagnosis
- Detects variants in genes like GBA (Gaucher Disease)
- Provides enzyme replacement therapy recommendations
- Outlines monitoring requirements

### Cardiovascular Risk
- Identifies Factor V Leiden mutations
- Recommends anticoagulation strategies
- Prevention guidelines

## 👥 Team SeqSleuths

Built for Convergence 2026 Symposium

## 📄 License

Educational project - Convergence 2026 Hackathon

---

**Questions?** Contact the team or visit our [GitHub repository](https://github.com/AleenaI20/GenoInsight)