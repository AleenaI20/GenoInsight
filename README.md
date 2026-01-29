# GenoInsight: AI-Powered Precision Medicine Platform

**Team SeqSleuths** | Convergence 2026 Hackathon | Northeastern University

---

## 👥 Team

- **Aleena Iraqui** - Full-stack development (ML pipeline, API, dashboard, presentation)
- **Nithisha Luther Bastin** - Clinical validation & regulatory documentation
- **Sudharsini Venugopal** - Team logistics & presentation coordination

---

## 🎯 Problem

1. **Fragmented data** - Clinical, genomic, lab results scattered across systems
2. **Variant overload** - 20,000+ variants per patient; identifying the 5-10 relevant ones takes days
3. **Communication gap** - Technical results inaccessible to clinicians and patients

---

## 💡 Solution

**GenoInsight** - End-to-end precision medicine platform

**1. AI Variant Hunter**
- Random Forest ML classifier
- Features: consequence severity, allele frequency, gnomAD pLI gene scores
- Training: 300 ClinVar-pattern variants

**2. Clinical Translation Engine**
- FDA pharmacogenomics database
- **gnomAD population frequencies** (African, Asian, European, Hispanic, Middle Eastern, South Asian)
- ACMG guideline compliance

**3. Interactive Dashboard**
- VCF file upload with ancestry tracking
- Multi-patient batch processing
- Real-time analysis with population-aware interpretation

---

## 🚀 Quick Start
```powershell
git clone https://github.com/AleenaI20/GenoInsight.git
cd GenoInsight
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python backend\api.py
# Open frontend\dashboard.html in browser
```

---

## 🧬 Key Features

✅ **VCF upload** - Accept patient files with ancestry information  
✅ **gnomAD integration** - Population-specific allele frequencies for 6 major populations  
✅ **Batch processing** - Analyze multiple patients simultaneously  
✅ **FDA drug matching** - PARP inhibitors (BRCA), EGFR TKIs, and more  
✅ **ML classification** - Real gnomAD pLI gene constraint scores  
✅ **Clinical reports** - Complete variant annotations with treatment recommendations  

---

## 📊 Technical Implementation

**Machine Learning:**
- Random Forest (100 trees, balanced classes)
- Training: ClinVar-style pathogenic/benign patterns
- Features: 5 (consequence, frequency, gene constraint, quality, coding)
- Gene scores: Real gnomAD pLI values (TP53=1.0, BRCA1=0.0)

**Population Genomics:**
- gnomAD v3.1.2-style frequency database
- 10 population groups tracked
- Ancestry-aware variant interpretation
- Reduces bias in pathogenicity prediction

**Clinical Databases:**
- FDA pharmacogenomics (drug-gene pairs)
- ClinGen/OMIM disease associations
- ACMG classification guidelines

---

## 🌍 Population Diversity

**Integrated gnomAD Data:**
- African/African American
- East Asian
- South Asian
- Non-Finnish European
- Hispanic/Latino
- Middle Eastern
- Finnish
- Ashkenazi Jewish
- Amish
- Other

**Impact:** Different populations have different allele frequencies. A variant rare in Europeans may be common in Africans. Our platform accounts for this.

---

## 📁 Structure
```
GenoInsight/
├── backend/
│   ├── variant_parser.py
│   ├── ml_classifier.py
│   ├── clinical_annotator.py
│   ├── gnomad_data.py         # Population frequencies
│   └── api.py
├── data/
│   └── sample_variants.vcf
├── models/
│   └── pathogenicity_model.pkl
└── frontend/
    └── dashboard.html
```

---

## 🛡️ Standards

- ✅ ACMG variant classification
- ✅ FDA pharmacogenomics
- ✅ gnomAD population genomics
- ✅ Population diversity tracking
- ⚠️ For Research Use Only

---

## 📜 License

MIT License | Copyright (c) 2026 Team SeqSleuths
