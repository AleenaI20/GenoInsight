let currentPatientId = null;
let allPatients = [];
let currentPatientVariants = [];

// Tab switching
function switchMainTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.style.display = 'none');
    document.querySelectorAll('[id^="tab-"]').forEach(tab => {
        tab.classList.remove('tab-active');
        tab.classList.add('text-gray-600', 'hover:text-indigo-600');
    });
    
    document.getElementById('content-' + tabName).style.display = 'block';
    const activeTab = document.getElementById('tab-' + tabName);
    activeTab.classList.add('tab-active');
    activeTab.classList.remove('text-gray-600', 'hover:text-indigo-600');

    if (tabName === 'pharmacogenomics') loadPharmacogenomics();
    if (tabName === 'bulk-analysis') loadBulkAnalysisOptions();
    if (tabName === 'statistics') loadStatistics();
}

// Load patients
async function loadPatients() {
    const response = await fetch('/api/patients');
    allPatients = await response.json();
    
    const grid = document.getElementById('patientGrid');
    grid.innerHTML = allPatients.map(patient => `
        <button onclick="selectPatient('${patient.id}')" 
                class="p-4 rounded-lg border-2 border-gray-200 hover:border-indigo-500 hover:shadow-lg transition-all text-left"
                id="patient-${patient.id}">
            <p class="font-bold text-sm text-gray-800">${patient.id}</p>
            <p class="text-xs text-gray-600 truncate">${patient.name}</p>
            <p class="text-xs mt-1">${patient.ancestry}</p>
            <p class="text-xs font-medium mt-1 ${
                patient.risk === 'High' ? 'text-red-600' : 
                patient.risk === 'Moderate' ? 'text-orange-600' : 'text-green-600'
            }">${patient.risk} Risk</p>
        </button>
    `).join('');
}

// Select patient
async function selectPatient(patientId) {
    currentPatientId = patientId;
    
    document.querySelectorAll('[id^="patient-"]').forEach(el => {
        el.classList.remove('border-indigo-600', 'bg-indigo-50');
        el.classList.add('border-gray-200');
    });
    document.getElementById(`patient-${patientId}`).classList.add('border-indigo-600', 'bg-indigo-50');
    
    const response = await fetch(`/api/patient/${patientId}/variants`);
    const data = await response.json();
    currentPatientVariants = data.variants;
    
    document.getElementById('patientName').textContent = data.patient.name;
    document.getElementById('patientInfo').textContent = 
        `Patient ID: ${data.patient.id} | Age: ${data.patient.age} | Ancestry: ${data.patient.ancestry}`;
    document.getElementById('totalVariants').textContent = data.totalVariants.toLocaleString();
    
    document.getElementById('snpCount').textContent = data.variantTypes.SNP;
    document.getElementById('indelCount').textContent = data.variantTypes.Indel;
    document.getElementById('svCount').textContent = data.variantTypes.SV;
    
    displayVariants(data.variants);
    displayDrugRecommendations(data.drugRecommendations);
    
    document.getElementById('patientDetails').style.display = 'block';
}

function displayVariants(variants) {
    const variantsList = document.getElementById('variantsList');
    variantsList.innerHTML = variants.map((v, idx) => {
        const pathClass = 
            v.pathogenicity === 'Pathogenic' ? 'badge-pathogenic' :
            v.pathogenicity === 'Risk Factor' ? 'badge-risk' :
            v.pathogenicity === 'Pharmacogenomic' ? 'badge-pharma' : 'badge-uncertain';
        
        return `
        <div class="border-2 border-gray-200 rounded-lg p-5 hover:border-indigo-300 hover:shadow-lg transition-all">
            <div class="flex items-start justify-between">
                <div class="flex-1">
                    <div class="flex items-center gap-3 mb-3 flex-wrap">
                        <span class="font-mono text-sm font-bold text-indigo-600 bg-indigo-50 px-3 py-1 rounded">${v.id}</span>
                        <span class="font-bold text-gray-800 text-lg">${v.gene}</span>
                        <span class="px-3 py-1 rounded-full text-xs font-semibold ${pathClass}">${v.pathogenicity}</span>
                        <span class="text-xs text-gray-500 bg-gray-100 px-3 py-1 rounded-full">${v.type}</span>
                        ${v.inheritance ? `<span class="text-xs text-purple-600 bg-purple-50 px-3 py-1 rounded-full">${v.inheritance}</span>` : ''}
                    </div>
                    
                    <div class="mb-3">
                        <p class="text-base font-semibold text-gray-800 mb-1">🏥 ${v.disease}</p>
                        <p class="text-xs text-gray-600 font-mono mb-1">📍 ${v.position}</p>
                        <p class="text-xs text-gray-600 font-mono">🧬 ${v.ref} → ${v.alt}</p>
                        ${v.hgvs ? `<p class="text-xs text-gray-500 mt-1">HGVS: ${v.hgvs}</p>` : ''}
                        ${v.clinvar_id ? `<p class="text-xs text-gray-500">ClinVar: ${v.clinvar_id}</p>` : ''}
                    </div>

                    ${v.drug ? `
                    <div class="bg-blue-50 border-l-4 border-blue-500 p-3 mb-3">
                        <p class="text-sm font-semibold text-blue-800">💊 Drug: ${v.drug}</p>
                        <p class="text-xs text-blue-700 mt-1">⚕️ ${v.recommendation}</p>
                    </div>
                    ` : ''}
                    
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mt-3">
                        <div class="bg-green-50 p-3 rounded-lg border border-green-200">
                            <p class="text-xs text-gray-600 mb-1">Random Forest</p>
                            <p class="font-bold text-green-700 text-lg">${(v.predictions.randomForest * 100).toFixed(1)}%</p>
                        </div>
                        <div class="bg-blue-50 p-3 rounded-lg border border-blue-200">
                            <p class="text-xs text-gray-600 mb-1">Logistic Reg</p>
                            <p class="font-bold text-blue-700 text-lg">${(v.predictions.logisticRegression * 100).toFixed(1)}%</p>
                        </div>
                        <div class="bg-purple-50 p-3 rounded-lg border border-purple-200">
                            <p class="text-xs text-gray-600 mb-1">XGBoost</p>
                            <p class="font-bold text-purple-700 text-lg">${(v.predictions.xgboost * 100).toFixed(1)}%</p>
                        </div>
                        <div class="bg-indigo-50 p-3 rounded-lg border-2 border-indigo-400">
                            <p class="text-xs text-gray-600 mb-1">Consensus</p>
                            <p class="font-bold text-indigo-700 text-lg">${(v.predictions.consensus * 100).toFixed(1)}%</p>
                        </div>
                    </div>
                </div>
                <div class="ml-6 text-right bg-gray-50 p-4 rounded-lg">
                    <p class="text-xs text-gray-500 mb-1">gnomAD Frequency</p>
                    ${v.gnomad_af ? `
                        <p class="font-semibold text-gray-700">${(v.gnomad_af.total * 100).toFixed(3)}%</p>
                        <div class="mt-2 text-xs space-y-1">
                            <p class="text-gray-600">AFR: ${(v.gnomad_af.african * 100).toFixed(3)}%</p>
                            <p class="text-gray-600">EUR: ${(v.gnomad_af.european * 100).toFixed(3)}%</p>
                            <p class="text-gray-600">EAS: ${(v.gnomad_af.east_asian * 100).toFixed(3)}%</p>
                            <p class="text-gray-600">SAS: ${(v.gnomad_af.south_asian * 100).toFixed(3)}%</p>
                        </div>
                    ` : '<p class="text-xs text-gray-500">N/A</p>'}
                </div>
            </div>
        </div>
        `;
    }).join('');
}

function displayDrugRecommendations(recommendations) {
    const drugsList = document.getElementById('patientDrugsList');
    
    if (recommendations.length === 0) {
        drugsList.innerHTML = '<p class="text-gray-600">No pharmacogenomic variants found for this patient.</p>';
        return;
    }
    
    drugsList.innerHTML = recommendations.map(rec => `
        <div class="border-2 border-blue-200 rounded-lg p-4 mb-4 bg-blue-50">
            <div class="flex items-start justify-between">
                <div class="flex-1">
                    <div class="flex items-center gap-3 mb-2">
                        <span class="font-mono text-sm font-bold text-blue-700">${rec.variant}</span>
                        <span class="font-bold text-gray-800">${rec.gene}</span>
                        <span class="px-3 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-800">${rec.actionability} Actionability</span>
                    </div>
                    <p class="text-sm font-semibold text-blue-900 mb-2">💊 Drug: ${rec.drug}</p>
                    <p class="text-sm text-blue-800">⚕️ Recommendation: ${rec.recommendation}</p>
                    <p class="text-xs text-blue-600 mt-2">📚 Evidence: ${rec.evidence}</p>
                </div>
            </div>
        </div>
    `).join('');
}

// Pharmacogenomics tab
function loadPharmacogenomics() {
    const content = document.getElementById('pharmacogenomicsContent');
    content.innerHTML = `
        <div class="bg-gradient-to-r from-purple-50 to-blue-50 border-2 border-purple-300 rounded-lg p-6 mb-6">
            <h3 class="text-xl font-bold text-purple-900 mb-3">🎯 Pharmacogenomics Overview</h3>
            <p class="text-gray-700 mb-4">GenoInsight analyzes key pharmacogenes to provide personalized drug recommendations based on genetic variants. This reduces adverse drug reactions and improves treatment efficacy.</p>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="bg-white p-3 rounded-lg shadow">
                    <p class="text-sm text-gray-600">Genes Analyzed</p>
                    <p class="text-2xl font-bold text-purple-700">8</p>
                </div>
                <div class="bg-white p-3 rounded-lg shadow">
                    <p class="text-sm text-gray-600">Drug Classes</p>
                    <p class="text-2xl font-bold text-blue-700">12</p>
                </div>
                <div class="bg-white p-3 rounded-lg shadow">
                    <p class="text-sm text-gray-600">Variants Tested</p>
                    <p class="text-2xl font-bold text-green-700">8</p>
                </div>
                <div class="bg-white p-3 rounded-lg shadow">
                    <p class="text-sm text-gray-600">Guidelines</p>
                    <p class="text-2xl font-bold text-orange-700">CPIC</p>
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="border-2 border-gray-200 rounded-lg p-5">
                <h4 class="font-bold text-lg mb-3">CYP2C9 - Warfarin Metabolism</h4>
                <p class="text-sm text-gray-600 mb-3">Variants affect warfarin dosing requirements</p>
                <div class="space-y-2 text-sm">
                    <div class="flex justify-between"><span>*1/*1 (Normal):</span><span class="font-semibold">Standard dose</span></div>
                    <div class="flex justify-between"><span>*1/*2 or *1/*3:</span><span class="font-semibold text-orange-600">Reduce 25-50%</span></div>
                    <div class="flex justify-between"><span>*2/*2, *2/*3, *3/*3:</span><span class="font-semibold text-red-600">Reduce 50-75%</span></div>
                </div>
            </div>

            <div class="border-2 border-gray-200 rounded-lg p-5">
                <h4 class="font-bold text-lg mb-3">CYP2C19 - Clopidogrel Response</h4>
                <p class="text-sm text-gray-600 mb-3">Poor metabolizers at higher cardiovascular risk</p>
                <div class="space-y-2 text-sm">
                    <div class="flex justify-between"><span>*1/*1 (Normal):</span><span class="font-semibold">Standard therapy</span></div>
                    <div class="flex justify-between"><span>*1/*2 (Intermediate):</span><span class="font-semibold text-orange-600">Monitor closely</span></div>
                    <div class="flex justify-between"><span>*2/*2 (Poor):</span><span class="font-semibold text-red-600">Alternative drug</span></div>
                </div>
            </div>

            <div class="border-2 border-gray-200 rounded-lg p-5">
                <h4 class="font-bold text-lg mb-3">CYP2D6 - Codeine/Opioid Response</h4>
                <p class="text-sm text-gray-600 mb-3">Affects codeine conversion to morphine</p>
                <div class="space-y-2 text-sm">
                    <div class="flex justify-between"><span>Normal:</span><span class="font-semibold">Standard dosing</span></div>
                    <div class="flex justify-between"><span>Poor Metabolizer:</span><span class="font-semibold text-orange-600">Alternative pain mgmt</span></div>
                    <div class="flex justify-between"><span>Ultra-rapid:</span><span class="font-semibold text-red-600">Avoid codeine</span></div>
                </div>
            </div>

            <div class="border-2 border-gray-200 rounded-lg p-5">
                <h4 class="font-bold text-lg mb-3">MTHFR - Methotrexate Toxicity</h4>
                <p class="text-sm text-gray-600 mb-3">Increased toxicity risk with reduced function</p>
                <div class="space-y-2 text-sm">
                    <div class="flex justify-between"><span>C/C (Normal):</span><span class="font-semibold">Standard dosing</span></div>
                    <div class="flex justify-between"><span>C/T (Heterozygous):</span><span class="font-semibold text-orange-600">Folic acid supplement</span></div>
                    <div class="flex justify-between"><span>T/T (Homozygous):</span><span class="font-semibold text-red-600">High-dose folate</span></div>
                </div>
            </div>
        </div>
    `;
}

// Bulk analysis
function loadBulkAnalysisOptions() {
    const selection = document.getElementById('bulkPatientSelection');
    selection.innerHTML = allPatients.map(p => `
        <label class="flex items-center space-x-2 p-3 border-2 border-gray-200 rounded-lg hover:border-indigo-400 cursor-pointer">
            <input type="checkbox" class="bulk-patient-checkbox" value="${p.id}">
            <div class="flex-1">
                <p class="font-semibold text-sm">${p.name}</p>
                <p class="text-xs text-gray-600">${p.id} - ${p.ancestry}</p>
            </div>
        </label>
    `).join('');
}

async function runBulkAnalysis() {
    const checkboxes = document.querySelectorAll('.bulk-patient-checkbox:checked');
    const patientIds = Array.from(checkboxes).map(cb => cb.value);
    
    if (patientIds.length === 0) {
        alert('Please select at least one patient');
        return;
    }

    const response = await fetch('/api/bulk/analyze', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({patients: patientIds})
    });
    
    const data = await response.json();
    
    const resultsDiv = document.getElementById('bulkResultsContent');
    resultsDiv.innerHTML = `
        <div class="bg-green-50 border-2 border-green-300 rounded-lg p-4 mb-4">
            <p class="font-semibold text-green-800">✅ Analysis completed for ${data.results.length} patients</p>
        </div>
        <div class="overflow-x-auto">
            <table class="min-w-full bg-white border border-gray-300">
                <thead class="bg-gray-100">
                    <tr>
                        <th class="px-4 py-3 text-left text-sm font-semibold">Patient ID</th>
                        <th class="px-4 py-3 text-left text-sm font-semibold">Name</th>
                        <th class="px-4 py-3 text-left text-sm font-semibold">Total Variants</th>
                        <th class="px-4 py-3 text-left text-sm font-semibold">Pathogenic</th>
                        <th class="px-4 py-3 text-left text-sm font-semibold">Highest Risk Disease</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.results.map(r => `
                        <tr class="border-t hover:bg-gray-50">
                            <td class="px-4 py-3 text-sm font-mono">${r.patient_id}</td>
                            <td class="px-4 py-3 text-sm">${r.name}</td>
                            <td class="px-4 py-3 text-sm">${r.totalVariants}</td>
                            <td class="px-4 py-3 text-sm font-semibold text-red-600">${r.pathogenicVariants}</td>
                            <td class="px-4 py-3 text-sm">${r.highestRiskDisease}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
    
    document.getElementById('bulkResults').style.display = 'block';
}

// VCF Upload
document.addEventListener('DOMContentLoaded', function() {
    const vcfInput = document.getElementById('vcfFileInput');
    if (vcfInput) {
        vcfInput.addEventListener('change', async function(e) {
            const file = e.target.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('file', file);

            const uploadResults = document.getElementById('uploadResults');
            const uploadResultsContent = document.getElementById('uploadResultsContent');
            
            uploadResultsContent.innerHTML = '<div class="animate-pulse text-center py-8"><p class="text-lg">Analyzing VCF file...</p></div>';
            uploadResults.style.display = 'block';

            try {
                const response = await fetch('/api/upload/vcf', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (data.success) {
                    uploadResultsContent.innerHTML = `
                        <div class="bg-green-50 border-2 border-green-300 rounded-lg p-6 mb-4">
                            <p class="font-semibold text-green-800 text-lg">✅ VCF Analysis Complete!</p>
                            <div class="grid grid-cols-2 gap-4 mt-4">
                                <div><span class="text-gray-700">Variants Found:</span> <span class="font-bold text-lg">${data.variantsFound}</span></div>
                                <div><span class="text-gray-700">Pathogenic:</span> <span class="font-bold text-lg text-red-600">${data.pathogenicVariants}</span></div>
                            </div>
                        </div>
                        <div class="space-y-3">
                            ${data.variants.slice(0, 10).map(v => `
                                <div class="border rounded-lg p-4 ${v.matched ? 'border-green-300 bg-green-50' : 'border-gray-300'}">
                                    <div class="flex items-center gap-3">
                                        <span class="font-mono text-sm">${v.id}</span>
                                        <span>${v.chrom}:${v.pos}</span>
                                        <span class="text-xs bg-gray-200 px-2 py-1 rounded">${v.ref} → ${v.alt}</span>
                                        ${v.matched ? '<span class="text-xs bg-green-200 text-green-800 px-2 py-1 rounded">✓ Known variant</span>' : '<span class="text-xs bg-yellow-200 text-yellow-800 px-2 py-1 rounded">Unknown</span>'}
                                    </div>
                                    ${v.disease ? `<p class="text-sm mt-2 text-gray-700">${v.disease}</p>` : ''}
                                </div>
                            `).join('')}
                        </div>
                    `;
                } else {
                    uploadResultsContent.innerHTML = `<div class="bg-red-50 border-2 border-red-300 rounded-lg p-4"><p class="text-red-800">Error: ${data.error}</p></div>`;
                }
            } catch (error) {
                uploadResultsContent.innerHTML = `<div class="bg-red-50 border-2 border-red-300 rounded-lg p-4"><p class="text-red-800">Error uploading file: ${error.message}</p></div>`;
            }
        });
    }
});

// Load statistics
async function loadStatistics() {
    const response = await fetch('/api/statistics');
    const stats = await response.json();

    document.getElementById('totalVariantsCount').textContent = stats.totalVariants.toLocaleString();
    document.getElementById('pharmaCount').textContent = stats.pharmacogenomicVariants;

    // Variant Type Chart
    new Chart(document.getElementById('variantTypeChart'), {
        type: 'doughnut',
        data: {
            labels: ['SNPs', 'Indels', 'Structural Variants'],
            datasets: [{
                data: [stats.variantTypes.SNPs, stats.variantTypes.Indels, stats.variantTypes.SVs],
                backgroundColor: ['#3b82f6', '#10b981', '#f59e0b']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });

    // Disease Category Chart
    new Chart(document.getElementById('diseaseCategoryChart'), {
        type: 'bar',
        data: {
            labels: ['Rare', 'Common', 'Cancer', 'Cardiovascular', 'Neurological'],
            datasets: [{
                label: 'Number of Diseases',
                data: [stats.diseases.rare, stats.diseases.common, stats.diseases.cancer, stats.diseases.cardiovascular, stats.diseases.neurological],
                backgroundColor: '#6366f1'
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    // Population Chart
    new Chart(document.getElementById('populationChart'), {
        type: 'pie',
        data: {
            labels: ['African', 'European', 'East Asian', 'South Asian', 'Hispanic/Latino'],
            datasets: [{
                data: [23, 28, 19, 15, 15],
                backgroundColor: ['#ef4444', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}

// Initialize
loadPatients();