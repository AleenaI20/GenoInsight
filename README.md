# GenoInsight: AI-Powered Precision Medicine Platform

**Team SeqSleuths** | Convergence 2026 Hackathon | Northeastern University

---

## 👥 Team

- **Aleena Iraqui** - Full-stack development (ML pipeline, API, dashboard, presentation)
- **Nithisha Luther Bastin** - Clinical validation & regulatory documentation
- **Sudharsini Venugopal** - Team logistics & presentation coordination

---

## 🎯 Problem

Healthcare faces three gaps in precision medicine:
1. **Fragmented data** - Clinical records, genomic data, lab results in separate systems
2. **Variant overload** - 20,000+ variants per patient; only 5-10 are clinically relevant
3. **Communication breakdown** - Technical results inaccessible to clinicians and patients

---

## 💡 Solution

GenoInsight platform with three components:

**1. AI Variant Hunter**
- Random Forest ML classifier for pathogenicity prediction
- Features: consequence severity, allele frequency, gene constraint, quality, coding status
- Output: 5-tier classification (Pathogenic → Benign)

**2. Clinical Translation Engine**
- FDA pharmacogenomics database (BRCA1→Olaparib, EGFR→Osimertinib)
- Disease associations from ClinGen/OMIM
- ACMG guideline compliance

**3. Interactive Dashboard**
- Multi-patient batch processing
- VCF file upload capability
- Real-time ML classification
- Full clinical report generation
- Population diversity tracking

---

## 🚀 Quick Start
```powershell
# Clone and setup
git clone https://github.com/AleenaI20/GenoInsight.git
cd GenoInsight
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run
python backend\api.py
# Then open frontend\dashboard.html in browser
```

---

## 📁 Structure
```
GenoInsight/
├── backend/
│   ├── variant_parser.py      # VCF parsing
│   ├── ml_classifier.py       # ML model
│   ├── clinical_annotator.py  # Clinical databases
│   └── api.py                 # Flask REST API
├── data/
│   └── sample_variants.vcf    # 20 cancer variants
├── models/
│   └── pathogenicity_model.pkl # Trained Random Forest
└── frontend/
    └── dashboard.html         # Interactive UI
```

---

## 🧬 Features

✅ Upload VCF files or select from database  
✅ Multi-patient batch analysis  
✅ ML pathogenicity prediction  
✅ FDA drug matching (PARP inhibitors, EGFR TKIs)  
✅ Disease risk assessment  
✅ Full clinical reports  
✅ Population diversity tracking (African, Asian, European, Hispanic, Middle Eastern, South Asian)  

---

## 📊 Sample Data

**20 variants** across cancer genes: BRCA1, BRCA2, TP53, EGFR, KRAS, PTEN, ATM, MLH1, MSH2, APC

**8 patient profiles** representing diverse ancestries

---

## 🛡️ Standards & Compliance

- ACMG variant classification guidelines
- FDA pharmacogenomics standards
- Population diversity awareness
- **For Research Use Only** (not FDA-approved)

---

## ⚠️ Limitations

- ML trained on simulated data (production requires ClinVar validation)
- Localhost demo (cloud deployment needed for multi-site access)
- 20 genes in current dataset (clinical panels have 50-500)
- Population-specific allele frequencies need gnomAD integration

---

## 📜 License

MIT License | Copyright (c) 2026 Team SeqSleuths
