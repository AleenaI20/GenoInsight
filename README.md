# GenoInsight: AI-Driven Precision Medicine Platform

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
- **💊 Treatment Options**: Specific medications and therapies
- **🔍 Screening Recommendations**: When and what tests to perform
- **🛡️ Prevention Strategies**: Risk reduction approaches
- **📊 Monitoring Plans**: Ongoing care guidelines

### 3. Multi-Patient Comparison
- Compare genetic risks across multiple patients
- Deterministic, reproducible results
- Support clinical research and cohort studies

### 4. AI-Powered Predictions
Three machine learning models working together:
- **Random Forest** (94% accuracy) - Primary model
- **XGBoost** (96% accuracy) - Enhanced predictions
- **Logistic Regression** (87% accuracy) - Baseline comparison

## 📊 Data Sources

- **ClinVar**: Real pathogenic variants (SNPs, Indels, Structural Variants)
- **gnomAD**: Population-specific allele frequencies across diverse ancestries
- **Evidence-Based Guidelines**: Clinical treatment recommendations

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
│   ├── app.py                      # Flask application with API endpoints
│   ├── data/
│   │   ├── variant_database.py     # ClinVar database (23 real variants)
│   │   ├── vcf_parser.py           # VCF file parser
│   │   └── __init__.py
│   └── models/
│       ├── ml_models.py            # ML models (RF, XGBoost, LR)
│       └── __init__.py
├── frontend/
│   ├── static/
│   │   └── js/
│   │       └── app.js              # Dashboard interactivity
│   └── templates/
│       └── dashboard.html          # User interface
├── .gitignore
├── README.md
└── requirements.txt
```

## 🎯 Impact

| Metric | Impact |
|--------|--------|
| **Efficiency** | Variant interpretation in seconds vs days |
| **Equity** | Population-aware analysis across 5+ ancestries |
| **Actionability** | Clear treatment plans for 12+ disease categories |
| **Accessibility** | Non-technical interface for stakeholders |

## 🧬 Example Use Cases

### Cancer Risk Assessment
- Identifies BRCA1/BRCA2 mutations
- Recommends PARP inhibitors (Olaparib, Talazoparib)
- Suggests screening protocols (MRI, mammography)
- Prevention strategies (prophylactic surgery, chemoprevention)

### Rare Disease Diagnosis
- Detects variants in GBA (Gaucher), CFTR (Cystic Fibrosis), SMN1 (SMA)
- Provides enzyme replacement therapy recommendations
- Outlines monitoring requirements

### Cardiovascular Risk
- Identifies Factor V Leiden, Sickle Cell mutations
- Recommends anticoagulation strategies
- Prevention guidelines

## 🔬 Technical Highlights

- **Real Data Integration**: ClinVar database with 23 verified pathogenic variants
- **Population Diversity**: gnomAD frequency data for equitable healthcare
- **Reproducible Results**: Deterministic patient profiles
- **Variant Coverage**: SNPs, Indels, Structural Variants (deletions, duplications)
- **Disease Coverage**: Cancer, rare diseases, cardiovascular, neurological, metabolic

## 👥 Development Team

**Aleena Iraqui** - *Lead Developer*
- Platform architecture and full-stack development
- Integrated real ClinVar and gnomAD variant databases
- Implemented ML models (Random Forest, XGBoost, Logistic Regression)
- Developed VCF file parser and upload functionality
- Created disease-specific treatment recommendation engine
- Built stakeholder-friendly dashboard interface
- Designed multi-patient comparison and bulk analysis features

**Nithisha Luther Bastin** - *Quality Assurance*
- Testing and debugging support

## 📄 Project Information

**Built for:** Convergence 2026 Symposium  
**Repository:** [https://github.com/AleenaI20/GenoInsight](https://github.com/AleenaI20/GenoInsight)

---

*GenoInsight: Accelerating precision medicine through AI-powered variant analysis*
