import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import json
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io
import base64

# Configure page
st.set_page_config(
    page_title="PediaSafeAI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling
st.markdown("""
<style>
.main-header {
    text-align: center;
    padding: 3rem 1rem;
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #ffffff 100%);
    color: white;
    margin: -1rem -1rem 3rem -1rem;
    border-radius: 0 0 20px 20px;
    box-shadow: 0 4px 15px rgba(30, 60, 114, 0.3);
}

.app-title {
    font-size: 3.5rem;
    font-weight: bold;
    margin-bottom: 1rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.credentials {
    font-size: 1.3rem;
    font-style: italic;
    margin-bottom: 1.5rem;
    opacity: 0.95;
}

.description {
    font-size: 1.2rem;
    max-width: 900px;
    margin: 0 auto;
    line-height: 1.7;
    opacity: 0.9;
}

.enter-button {
    text-align: center;
    margin: 3rem 0;
}

.input-section {
    background: linear-gradient(145deg, #f8fbff 0%, #e8f4fd 100%);
    padding: 2rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    border: 2px solid #c3d9ff;
    box-shadow: 0 4px 10px rgba(30, 60, 114, 0.1);
}

.input-section h3 {
    color: #1e3c72;
    margin-bottom: 1.5rem;
    font-weight: 600;
}

.screening-results-header {
    text-align: center;
    font-size: 2.5rem;
    color: #1e3c72;
    margin: 3rem 0;
    font-weight: 600;
}

.metrics-container {
    margin: 2rem 0 3rem 0;
}

.tabs-container {
    margin: 2rem 0;
}

.result-card {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    margin-bottom: 2rem;
    border-left: 5px solid #dc3545;
}

.result-card.warning {
    border-left-color: #ffc107;
}

.result-card.success {
    border-left-color: #28a745;
}

.footer {
    text-align: center;
    padding: 2rem;
    background: linear-gradient(145deg, #f0f7ff 0%, #e0efff 100%);
    margin: 3rem -1rem -1rem -1rem;
    border-top: 3px solid #c3d9ff;
    color: #1e3c72;
    font-weight: 500;
}

.disclaimer-container {
    text-align: center;
    margin: 3rem 0 2rem 0;
}

.disclaimer-content {
    background: linear-gradient(145deg, #fff8e1 0%, #ffecb3 100%);
    border: 2px solid #ffcc02;
    border-radius: 10px;
    padding: 1.5rem;
    margin: 1rem auto;
    max-width: 800px;
    text-align: left;
}

.download-section {
    margin: 3rem 0;
    padding: 2rem;
    background: linear-gradient(145deg, #f0f7ff 0%, #e8f4fd 100%);
    border-radius: 15px;
    border: 2px solid #c3d9ff;
}

.stButton > button {
    background: linear-gradient(145deg, #1e3c72 0%, #2a5298 100%);
    color: white;
    font-weight: bold;
    border: none;
    padding: 0.7rem 2rem;
    border-radius: 8px;
    font-size: 1.1rem;
}

.stButton > button:hover {
    background: linear-gradient(145deg, #2a5298 0%, #1e3c72 100%);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(30, 60, 114, 0.3);
}
</style>
""", unsafe_allow_html=True)

# Database classes
class PediatricDrugDatabase:
    def __init__(self):
        self.popi_criteria = self._load_popi_criteria()
        self.pipc_criteria = self._load_pipc_criteria()
        self.kids_list = self._load_kids_list()
        self.common_medications = self._load_common_medications()
        self.common_conditions = self._load_common_conditions()

    def _load_popi_criteria(self):
        """POPI (Pediatrics: Omission of Prescriptions and Inappropriate prescriptions) criteria"""
        return {
            "inappropriate": [
                {
                    "medication": "Aspirin",
                    "age_restriction": "< 16 years",
                    "condition": "Any condition except Kawasaki disease",
                    "rationale": "Risk of Reye's syndrome in children under 16 years",
                    "reference": "POPI explicit criteria - Reye's syndrome prevention"
                },
                {
                    "medication": "Codeine",
                    "age_restriction": "< 12 years",
                    "condition": "Pain management or cough suppression",
                    "rationale": "Risk of serious respiratory depression due to variable CYP2D6 metabolism",
                    "reference": "FDA Safety Communication 2013, POPI criteria"
                },
                {
                    "medication": "Tramadol",
                    "age_restriction": "< 12 years",
                    "condition": "Pain management",
                    "rationale": "Risk of serious respiratory depression, especially in ultra-rapid CYP2D6 metabolizers",
                    "reference": "FDA Safety Communication 2017, POPI criteria"
                },
                {
                    "medication": "Diphenhydramine",
                    "age_restriction": "< 2 years",
                    "condition": "Any condition",
                    "rationale": "Risk of anticholinergic toxicity and paradoxical excitation in infants",
                    "reference": "POPI explicit criteria, AAP recommendations"
                },
                {
                    "medication": "Promethazine",
                    "age_restriction": "< 2 years",
                    "condition": "Any condition",
                    "rationale": "Risk of severe respiratory depression and death",
                    "reference": "FDA Black Box Warning, POPI criteria"
                },
                {
                    "medication": "Dextromethorphan",
                    "age_restriction": "< 4 years",
                    "condition": "Cough",
                    "rationale": "Limited efficacy and potential for serious adverse effects including respiratory depression",
                    "reference": "AAP Clinical Report 2008, POPI criteria"
                },
                {
                    "medication": "Pseudoephedrine",
                    "age_restriction": "< 4 years",
                    "condition": "Nasal congestion",
                    "rationale": "Risk of cardiovascular and CNS adverse effects with minimal efficacy",
                    "reference": "POPI criteria, FDA recommendations"
                },
                {
                    "medication": "Phenylephrine",
                    "age_restriction": "< 4 years",
                    "condition": "Nasal congestion",
                    "rationale": "Risk of hypertension and cardiovascular effects in young children",
                    "reference": "POPI explicit criteria"
                },
                {
                    "medication": "Loperamide",
                    "age_restriction": "< 2 years",
                    "condition": "Diarrhea",
                    "rationale": "Risk of paralytic ileus and CNS depression in young children",
                    "reference": "POPI criteria, WHO recommendations"
                },
                {
                    "medication": "Metoclopramide",
                    "age_restriction": "< 1 year",
                    "condition": "Any condition",
                    "rationale": "Risk of extrapyramidal symptoms and tardive dyskinesia",
                    "reference": "POPI explicit criteria, EMA recommendations"
                }
            ]
        }

    def _load_pipc_criteria(self):
        """Pediatric Inappropriate Prescribing Criteria - Comprehensive omissions list"""
        return {
            "omissions": [
                {
                    "condition": "Asthma",
                    "missing_medication": "Short-acting beta-2 agonist (Salbutamol)",
                    "rationale": "Essential rescue medication for acute bronchospasm in all asthma patients",
                    "reference": "GINA Guidelines 2023, PIPc criteria"
                },
                {
                    "condition": "ADHD",
                    "missing_medication": "Methylphenidate or Amphetamine",
                    "rationale": "First-line pharmacological treatment for ADHD in children over 6 years",
                    "reference": "AAP Clinical Practice Guidelines, PIPc criteria"
                },
                {
                    "condition": "Seizure disorder",
                    "missing_medication": "Anti-epileptic drug",
                    "rationale": "Essential for seizure prevention and control to prevent status epilepticus",
                    "reference": "ILAE Guidelines, PIPc criteria"
                },
                {
                    "condition": "Epilepsy",
                    "missing_medication": "Anti-epileptic drug",
                    "rationale": "Mandatory for seizure control and prevention of neurological damage",
                    "reference": "ILAE Guidelines, PIPc criteria"
                },
                {
                    "condition": "Type 1 Diabetes",
                    "missing_medication": "Insulin",
                    "rationale": "Life-essential hormone replacement therapy for survival",
                    "reference": "ADA Pediatric Guidelines, PIPc criteria"
                },
                {
                    "condition": "Bacterial pneumonia",
                    "missing_medication": "Appropriate antibiotic",
                    "rationale": "Essential for treating bacterial infection and preventing complications",
                    "reference": "WHO pneumonia guidelines, PIPc criteria"
                },
                {
                    "condition": "Urinary tract infection",
                    "missing_medication": "Appropriate antibiotic",
                    "rationale": "Necessary to prevent progression to pyelonephritis and sepsis",
                    "reference": "AAP UTI guidelines, PIPc criteria"
                },
                {
                    "condition": "Iron deficiency anemia",
                    "missing_medication": "Iron supplements",
                    "rationale": "Essential for correction of iron deficiency and anemia",
                    "reference": "AAP anemia guidelines, PIPc criteria"
                },
                {
                    "condition": "Congenital hypothyroidism",
                    "missing_medication": "Levothyroxine",
                    "rationale": "Critical for normal growth and neurodevelopment",
                    "reference": "AAP thyroid guidelines, PIPc criteria"
                },
                {
                    "condition": "Severe allergic reaction",
                    "missing_medication": "Epinephrine",
                    "rationale": "Life-saving treatment for anaphylaxis",
                    "reference": "Anaphylaxis guidelines, PIPc criteria"
                }
            ]
        }

    def _load_kids_list(self):
        """KIDs List (Key potentially Inappropriate Drugs) - Comprehensive criteria"""
        return {
            "inappropriate": [
                {
                    "medication": "Chlorpheniramine",
                    "age_restriction": "< 2 years",
                    "condition": "Allergic conditions",
                    "rationale": "Risk of CNS depression and anticholinergic effects in young children",
                    "reference": "KIDs List criteria, FDA recommendations"
                },
                {
                    "medication": "Hyoscine",
                    "age_restriction": "< 6 months",
                    "condition": "Any condition",
                    "rationale": "Risk of anticholinergic toxicity in young infants",
                    "reference": "KIDs List criteria"
                },
                {
                    "medication": "Atropine",
                    "age_restriction": "< 6 months",
                    "condition": "Non-emergency use",
                    "rationale": "Risk of anticholinergic toxicity and hyperthermia in infants",
                    "reference": "KIDs List criteria"
                },
                {
                    "medication": "Domperidone",
                    "age_restriction": "< 12 years with cardiac conditions",
                    "condition": "Cardiac arrhythmias present",
                    "rationale": "Risk of QT prolongation and sudden cardiac death",
                    "reference": "KIDs List criteria, EMA warnings"
                },
                {
                    "medication": "Erythromycin",
                    "age_restriction": "< 2 weeks",
                    "condition": "Any condition",
                    "rationale": "Risk of pyloric stenosis in young infants",
                    "reference": "KIDs List criteria, FDA warnings"
                },
                {
                    "medication": "Ciprofloxacin",
                    "age_restriction": "< 18 years",
                    "condition": "Non-severe infections",
                    "rationale": "Risk of arthropathy and tendon damage in growing children",
                    "reference": "KIDs List criteria, FDA Black Box Warning"
                },
                {
                    "medication": "Levofloxacin",
                    "age_restriction": "< 18 years",
                    "condition": "Non-severe infections",
                    "rationale": "Risk of arthropathy and tendon damage in pediatric patients",
                    "reference": "KIDs List criteria, FDA warnings"
                },
                {
                    "medication": "Tetracycline",
                    "age_restriction": "< 8 years",
                    "condition": "Any condition",
                    "rationale": "Risk of permanent tooth discoloration and enamel hypoplasia",
                    "reference": "KIDs List criteria, standard pediatric references"
                },
                {
                    "medication": "Doxycycline",
                    "age_restriction": "< 8 years",
                    "condition": "Any condition except life-threatening infections",
                    "rationale": "Risk of permanent tooth discoloration and impaired bone growth",
                    "reference": "KIDs List criteria, AAP recommendations"
                },
                {
                    "medication": "Amiodarone",
                    "age_restriction": "All ages",
                    "condition": "First-line antiarrhythmic use",
                    "rationale": "Multiple serious adverse effects including thyroid, pulmonary, and hepatic toxicity",
                    "reference": "KIDs List criteria, pediatric cardiology guidelines"
                }
            ]
        }

    def _load_common_medications(self):
        """Comprehensive list of pediatric medications from POPI, PIPc, and KIDs list"""
        return [
            # Analgesics and Antipyretics
            "Paracetamol/Acetaminophen", "Ibuprofen", "Aspirin", "Codeine", "Tramadol", "Morphine",
            "Diclofenac", "Naproxen", "Celecoxib", "Indomethacin",
            
            # Antibiotics
            "Amoxicillin", "Amoxicillin/Clavulanate", "Azithromycin", "Clarithromycin", "Erythromycin",
            "Cephalexin", "Cefuroxime", "Ceftriaxone", "Ciprofloxacin", "Levofloxacin", "Clindamycin",
            "Vancomycin", "Gentamicin", "Tobramycin", "Cotrimoxazole/TMP-SMX",
            
            # Respiratory Medications
            "Salbutamol", "Terbutaline", "Fluticasone", "Budesonide", "Beclomethasone", "Montelukast",
            "Theophylline", "Prednisolone", "Dexamethasone", "Ipratropium", "Tiotropium",
            
            # Antihistamines and Allergy
            "Cetirizine", "Loratadine", "Fexofenadine", "Diphenhydramine", "Chlorpheniramine",
            "Promethazine", "Hydroxyzine", "Desloratadine", "Levocetirizine",
            
            # Cough and Cold
            "Dextromethorphan", "Guaifenesin", "Pseudoephedrine", "Phenylephrine",
            
            # Gastrointestinal
            "Omeprazole", "Lansoprazole", "Ranitidine", "Famotidine", "Domperidone", "Metoclopramide",
            "Ondansetron", "Loperamide", "Lactulose", "Polyethylene glycol", "Simethicone",
            
            # Neurological and Psychiatric
            "Methylphenidate", "Amphetamine", "Atomoxetine", "Risperidone", "Aripiprazole",
            "Phenytoin", "Carbamazepine", "Valproic acid", "Levetiracetam", "Lamotrigine",
            "Clonazepam", "Diazepam", "Lorazepam",
            
            # Cardiovascular
            "Digoxin", "Furosemide", "Spironolactone", "Captopril", "Enalapril", "Amlodipine",
            "Propranolol", "Atenolol", "Metoprolol",
            
            # Endocrine
            "Insulin", "Metformin", "Levothyroxine", "Prednisolone", "Hydrocortisone",
            
            # Dermatological
            "Hydrocortisone cream", "Betamethasone", "Calamine lotion", "Mupirocin",
            "Clotrimazole", "Nystatin", "Acyclovir",
            
            # Ophthalmological
            "Chloramphenicol eye drops", "Tobramycin eye drops", "Prednisolone eye drops",
            
            # Miscellaneous
            "Iron supplements", "Folic acid", "Vitamin D", "Multivitamins", "Zinc supplements",
            "ORS (Oral Rehydration Solution)", "Hyoscine", "Atropine", "Glycerin suppository"
        ]

    def _load_common_conditions(self):
        """Comprehensive list of pediatric conditions from POPI, PIPc, and KIDs list"""
        return [
            # Respiratory Conditions
            "Upper respiratory tract infection", "Asthma", "Bronchiolitis", "Pneumonia", 
            "Croup", "Chronic cough", "Allergic rhinitis", "Sinusitis",
            
            # Infectious Diseases
            "Acute otitis media", "Pharyngitis/Tonsillitis", "Urinary tract infection",
            "Gastroenteritis", "Skin and soft tissue infection", "Meningitis", "Sepsis",
            "Conjunctivitis", "Impetigo", "Cellulitis",
            
            # Gastrointestinal Disorders
            "GERD (Gastroesophageal reflux disease)", "Constipation", "Diarrhea", 
            "Inflammatory bowel disease", "Peptic ulcer disease", "Nausea and vomiting",
            "Abdominal pain", "Food poisoning",
            
            # Neurological and Psychiatric
            "ADHD (Attention Deficit Hyperactivity Disorder)", "Seizure disorder", "Epilepsy",
            "Febrile seizures", "Migraine", "Headache", "Autism spectrum disorder",
            "Anxiety disorder", "Depression", "Sleep disorders",
            
            # Allergic and Immunological
            "Eczema/Atopic dermatitis", "Food allergies", "Drug allergies", "Anaphylaxis",
            "Allergic conjunctivitis", "Contact dermatitis",
            
            # Endocrine and Metabolic
            "Type 1 Diabetes", "Type 2 Diabetes", "Hypothyroidism", "Hyperthyroidism",
            "Growth hormone deficiency", "Obesity", "Failure to thrive",
            
            # Cardiovascular
            "Congenital heart disease", "Hypertension", "Arrhythmias", "Heart failure",
            "Kawasaki disease", "Rheumatic fever",
            
            # Hematological and Oncological
            "Iron deficiency anemia", "Sickle cell disease", "Thalassemia", "Leukemia",
            "Lymphoma", "Bleeding disorders",
            
            # Musculoskeletal
            "Juvenile idiopathic arthritis", "Fractures", "Sprains and strains",
            "Muscular dystrophy", "Osteomyelitis",
            
            # Genitourinary
            "Nephrotic syndrome", "Chronic kidney disease", "Vesicoureteral reflux",
            "Enuresis (bedwetting)", "Urinary incontinence",
            
            # Dermatological
            "Diaper dermatitis", "Seborrheic dermatitis", "Psoriasis", "Acne",
            "Fungal infections", "Viral exanthems", "Scabies",
            
            # Others
            "Fever of unknown origin", "Pain management", "Palliative care",
            "Immunization reactions", "Poisoning/Overdose", "Burns"
        ]

class OpenFDAAPI:
    def __init__(self):
        self.base_url = "https://api.fda.gov/drug"
        self.adverse_events_url = f"{self.base_url}/event.json"
        self.drug_labels_url = f"{self.base_url}/label.json"
        
    def normalize_drug_name(self, drug_name):
        """Normalize drug name for API search"""
        # Remove common suffixes and normalize
        drug_name = drug_name.lower()
        drug_name = drug_name.replace("/acetaminophen", "").replace("/clavulanate", "")
        drug_name = drug_name.replace("paracetamol", "acetaminophen")
        drug_name = drug_name.split()[0]  # Take first word
        return drug_name.strip()
    
    def search_drug_interactions_fda(self, drug1, drug2):
        """Search for drug interactions using OpenFDA API"""
        try:
            # Normalize drug names
            drug1_norm = self.normalize_drug_name(drug1)
            drug2_norm = self.normalize_drug_name(drug2)
            
            # Search for adverse events involving both drugs
            search_query = f'patient.drug.medicinalproduct:"{drug1_norm}"+AND+patient.drug.medicinalproduct:"{drug2_norm}"'
            
            params = {
                'search': search_query,
                'count': 'patient.reaction.reactionmeddrapt.exact',
                'limit': 10
            }
            
            response = requests.get(self.adverse_events_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'results' in data and data['results']:
                    # Extract common adverse reactions
                    reactions = []
                    for result in data['results'][:5]:  # Top 5 reactions
                        reactions.append(result['term'])
                    
                    return {
                        'found': True,
                        'reactions': reactions,
                        'source': 'OpenFDA Adverse Events Database'
                    }
            
            return {'found': False}
            
        except Exception as e:
            print(f"OpenFDA API error: {e}")
            return {'found': False}
    
    def search_drug_labels_for_interactions(self, drug_name):
        """Search drug labels for interaction information"""
        try:
            drug_norm = self.normalize_drug_name(drug_name)
            
            params = {
                'search': f'openfda.brand_name:"{drug_norm}" OR openfda.generic_name:"{drug_norm}"',
                'limit': 1
            }
            
            response = requests.get(self.drug_labels_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'results' in data and data['results']:
                    label_data = data['results'][0]
                    
                    # Extract interaction information from various label sections
                    interactions_info = []
                    
                    # Check drug interactions section
                    if 'drug_interactions' in label_data:
                        interactions_info.extend(label_data['drug_interactions'])
                    
                    # Check contraindications
                    if 'contraindications' in label_data:
                        interactions_info.extend(label_data['contraindications'])
                    
                    # Check warnings and precautions
                    if 'warnings_and_cautions' in label_data:
                        interactions_info.extend(label_data['warnings_and_cautions'])
                    
                    return interactions_info
            
            return []
            
        except Exception as e:
            print(f"Drug labels API error: {e}")
            return []

    def check_drug_interactions(self, medications):
        """Check for drug-drug interactions using OpenFDA API and known interactions"""
        interactions = []
        
        # Known critical interactions database (for immediate results)
        critical_interactions = {
            ("warfarin", "aspirin"): {
                "severity": "Major",
                "mechanism": "Increased bleeding risk due to additive antiplatelet and anticoagulant effects",
                "management": "Avoid concurrent use or monitor closely with frequent INR checks and bleeding assessment",
                "clinical_significance": "High risk of major bleeding events"
            },
            ("digoxin", "amiodarone"): {
                "severity": "Major",
                "mechanism": "Amiodarone inhibits P-glycoprotein, increasing digoxin serum levels up to 2-fold",
                "management": "Reduce digoxin dose by 50% and monitor serum digoxin levels closely",
                "clinical_significance": "Risk of digoxin toxicity with cardiac arrhythmias"
            },
            ("phenytoin", "carbamazepine"): {
                "severity": "Major",
                "mechanism": "Mutual induction of hepatic enzymes leading to decreased efficacy of both drugs",
                "management": "Monitor seizure control and consider dose adjustments or alternative therapy",
                "clinical_significance": "Loss of seizure control in epileptic patients"
            },
            ("methotrexate", "trimethoprim"): {
                "severity": "Major", 
                "mechanism": "Both drugs inhibit folate metabolism, leading to additive bone marrow suppression",
                "management": "Avoid combination or increase folate supplementation with close monitoring",
                "clinical_significance": "Severe pancytopenia and immunosuppression"
            },
            ("theophylline", "ciprofloxacin"): {
                "severity": "Major",
                "mechanism": "Ciprofloxacin inhibits CYP1A2, reducing theophylline clearance by up to 30%",
                "management": "Reduce theophylline dose by 50% and monitor serum levels",
                "clinical_significance": "Risk of theophylline toxicity with seizures and cardiac arrhythmias"
            },
            ("insulin", "corticosteroids"): {
                "severity": "Moderate",
                "mechanism": "Corticosteroids increase blood glucose through gluconeogenesis and insulin resistance",
                "management": "Monitor blood glucose closely and adjust insulin dosing as needed",
                "clinical_significance": "Loss of glycemic control in diabetic patients"
            },
            ("acetaminophen", "warfarin"): {
                "severity": "Moderate",
                "mechanism": "High-dose acetaminophen may enhance anticoagulant effect of warfarin",
                "management": "Limit acetaminophen to <2g/day and monitor INR more frequently",
                "clinical_significance": "Increased bleeding risk with chronic high-dose use"
            },
            ("omeprazole", "clopidogrel"): {
                "severity": "Moderate",
                "mechanism": "Omeprazole inhibits CYP2C19, reducing conversion of clopidogrel to active metabolite",
                "management": "Consider alternative PPI (pantoprazole) or H2 blocker",
                "clinical_significance": "Reduced antiplatelet effect increasing cardiovascular risk"
            }
        }
        
        # Check all medication pairs
        for i, med1 in enumerate(medications):
            for j, med2 in enumerate(medications[i+1:], i+1):
                
                # Check critical interactions first
                pair1 = tuple(sorted([self.normalize_drug_name(med1), self.normalize_drug_name(med2)]))
                pair2 = (self.normalize_drug_name(med1), self.normalize_drug_name(med2))
                pair3 = (self.normalize_drug_name(med2), self.normalize_drug_name(med1))
                
                found_interaction = None
                for pair in [pair1, pair2, pair3]:
                    if pair in critical_interactions:
                        found_interaction = critical_interactions[pair]
                        break
                
                if found_interaction:
                    interactions.append({
                        "drug1": med1,
                        "drug2": med2,
                        "severity": found_interaction["severity"],
                        "mechanism": found_interaction["mechanism"],
                        "management": found_interaction["management"],
                        "clinical_significance": found_interaction["clinical_significance"],
                        "reference": "Clinical pharmacology database and FDA drug labels"
                    })
                else:
                    # Search OpenFDA API for potential interactions
                    fda_result = self.search_drug_interactions_fda(med1, med2)
                    
                    if fda_result.get('found'):
                        # Create interaction based on FDA adverse events data
                        reactions = fda_result.get('reactions', [])
                        if reactions:
                            interactions.append({
                                "drug1": med1,
                                "drug2": med2,
                                "severity": "Monitor",
                                "mechanism": f"Potential interaction based on reported adverse events: {', '.join(reactions[:3])}",
                                "management": "Monitor patient closely for unusual symptoms or side effects",
                                "clinical_significance": "Interaction reported in FDA adverse events database",
                                "reference": f"OpenFDA Adverse Events Database - {fda_result['source']}"
                            })
        
        return interactions

def generate_pdf_report(patient_age, indication, medications, inappropriate_meds, omissions, interactions):
    """Generate PDF report of screening results"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#667eea',
        alignment=1,  # Center alignment
        spaceAfter=20
    )
    story.append(Paragraph("🛡️ PediaSafeAI Screening Report", title_style))
    
    # Report details
    story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Paragraph(f"<b>Patient Age:</b> {patient_age}", styles['Normal']))
    story.append(Paragraph(f"<b>Indication:</b> {indication}", styles['Normal']))
    story.append(Paragraph(f"<b>Medications:</b> {', '.join(medications)}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Results sections
    sections = [
        ("Inappropriate Prescriptions", inappropriate_meds),
        ("Prescription Omissions", omissions),
        ("Drug-Drug Interactions", interactions)
    ]
    
    for section_title, results in sections:
        story.append(Paragraph(section_title, styles['Heading2']))
        if results:
            if section_title == "Drug-Drug Interactions":
                for result in results:
                    story.append(Paragraph(f"• {result.get('drug1', 'N/A')} ↔ {result.get('drug2', 'N/A')} ({result.get('severity', 'Unknown')} Interaction)", styles['Normal']))
                    story.append(Paragraph(f"  <i>Mechanism:</i> {result.get('mechanism', 'N/A')}", styles['Normal']))
                    story.append(Paragraph(f"  <i>Management:</i> {result.get('management', 'N/A')}", styles['Normal']))
                    if result.get('clinical_significance'):
                        story.append(Paragraph(f"  <i>Clinical Significance:</i> {result.get('clinical_significance')}", styles['Normal']))
                    story.append(Paragraph(f"  <i>Reference:</i> {result.get('reference', 'N/A')}", styles['Normal']))
                    story.append(Spacer(1, 10))
            else:
                for result in results:
                    story.append(Paragraph(f"• {result.get('medication', result.get('missing_medication', 'N/A'))}", styles['Normal']))
                    story.append(Paragraph(f"  <i>Rationale:</i> {result.get('rationale', 'N/A')}", styles['Normal']))
                    story.append(Paragraph(f"  <i>Reference:</i> {result.get('reference', 'N/A')}", styles['Normal']))
                    story.append(Spacer(1, 10))
        else:
            story.append(Paragraph("No issues identified.", styles['Normal']))
        story.append(Spacer(1, 15))
    
    # Footer
    story.append(Spacer(1, 30))
    story.append(Paragraph("Developed for pediatric medication safety • Always consult healthcare professionals for clinical decisions", styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def main():
    # Initialize databases
    if 'drug_db' not in st.session_state:
        st.session_state.drug_db = PediatricDrugDatabase()
        st.session_state.fda_api = OpenFDAAPI()
    
    # Initialize session state
    if 'show_app' not in st.session_state:
        st.session_state.show_app = False
    if 'screening_done' not in st.session_state:
        st.session_state.screening_done = False

    # Landing page
    if not st.session_state.show_app:
        st.markdown("""
        <div class="main-header">
            <div class="app-title">🛡️ PediaSafeAI</div>
            <div class="credentials">by Ayesha Bibi, MPhil Pharmacy Practice Student (GCUF)</div>
            <div class="description">
                An AI-driven clinical decision support system designed to screen pediatric prescriptions 
                for inappropriate use, omissions, and drug interactions to ensure safer pharmacotherapy.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Enter Application", type="primary", use_container_width=True):
                st.session_state.show_app = True
                st.rerun()
    
    # Main application
    else:
        # Header
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0; margin-bottom: 2rem;">
            <h1>🛡️ PediaSafeAI</h1>
            <p style="font-style: italic; color: #666;">by Ayesha Bibi, MPhil Pharmacy Practice Student (GCUF)</p>
            <p style="color: #888; max-width: 600px; margin: 0 auto;">
                An AI-driven clinical decision support system designed to screen pediatric prescriptions 
                for inappropriate use, omissions, and drug interactions to ensure safer pharmacotherapy.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state.screening_done:
            # Input form - vertical layout with proper spacing
            with st.form("screening_form"):
                # Patient Information Section
                st.markdown('<div class="input-section">', unsafe_allow_html=True)
                st.markdown("### Patient Information")
                
                col1, col2 = st.columns(2)
                with col1:
                    age_unit = st.selectbox("Age Unit", ["Years", "Months"])
                with col2:
                    patient_age_value = st.number_input("Patient Age", min_value=0, value=5)
                
                patient_age = f"{patient_age_value} {age_unit.lower()}"
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Add vertical spacing
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Clinical Information Section
                st.markdown('<div class="input-section">', unsafe_allow_html=True)
                st.markdown("### Clinical Information")
                
                indication = st.selectbox(
                    "Medical Condition/Indication",
                    [""] + st.session_state.drug_db.common_conditions,
                    help="Select the primary medical condition"
                )
                
                # Option to add custom indication
                custom_indication = st.text_input(
                    "Add custom indication (if not in list above)",
                    placeholder="Type custom medical condition here..."
                )
                
                if custom_indication:
                    indication = custom_indication
                    
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Add vertical spacing
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Current Medications Section
                st.markdown('<div class="input-section">', unsafe_allow_html=True)
                st.markdown("### Current Medications")
                
                selected_medications = st.multiselect(
                    "Select medications (you can select multiple)",
                    st.session_state.drug_db.common_medications,
                    help="Select all current medications for the patient"
                )
                
                # Option to add custom medications
                custom_medications = st.text_area(
                    "Add custom medications (if not in list above)",
                    placeholder="Enter additional medications, separated by commas...",
                    height=100
                )
                
                # Process custom medications
                if custom_medications:
                    custom_med_list = [med.strip() for med in custom_medications.split(',') if med.strip()]
                    selected_medications.extend(custom_med_list)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Add spacing before submit button
                st.markdown("<br><br>", unsafe_allow_html=True)
                
                # Submit button with bold styling
                submitted = st.form_submit_button(
                    "**🔍 SCREEN PRESCRIPTION**", 
                    type="primary", 
                    use_container_width=True
                )
                
                if submitted and selected_medications and indication:
                    # Perform screening
                    inappropriate_meds = []
                    omissions = []
                    interactions = st.session_state.fda_api.check_drug_interactions(selected_medications)
                    
                    # Check POPI criteria
                    age_in_years = patient_age_value if age_unit == "Years" else patient_age_value / 12
                    
                    for med in selected_medications:
                        # Check POPI criteria
                        for criteria in st.session_state.drug_db.popi_criteria["inappropriate"]:
                            if criteria["medication"].lower() in med.lower():
                                if check_age_restriction(criteria["age_restriction"], age_in_years):
                                    inappropriate_meds.append(criteria)
                        
                        # Check KIDs list criteria
                        for criteria in st.session_state.drug_db.kids_list["inappropriate"]:
                            if criteria["medication"].lower() in med.lower():
                                if check_age_restriction(criteria["age_restriction"], age_in_years):
                                    inappropriate_meds.append(criteria)
                    
                    # Check for omissions (PIPc criteria)
                    for omission in st.session_state.drug_db.pipc_criteria["omissions"]:
                        if omission["condition"].lower() in indication.lower():
                            # Check if the required medication is not in the list
                            required_med_found = any(
                                any(req_med.lower() in med.lower() for req_med in omission["missing_medication"].split(" or "))
                                for med in selected_medications
                            )
                            if not required_med_found:
                                omissions.append(omission)
                    
                    # Store results in session state
                    st.session_state.screening_results = {
                        'patient_age': patient_age,
                        'indication': indication,
                        'medications': selected_medications,
                        'inappropriate_meds': inappropriate_meds,
                        'omissions': omissions,
                        'interactions': interactions
                    }
                    st.session_state.screening_done = True
                    st.rerun()
                elif submitted:
                    if not selected_medications:
                        st.error("⚠️ Please select at least one medication.")
                    if not indication:
                        st.error("⚠️ Please select a medical condition.")
        
        else:
            # Display results with improved layout and spacing
            results = st.session_state.screening_results
            
            # Centered header with better spacing
            st.markdown('<div class="screening-results-header">📊 Screening Results</div>', unsafe_allow_html=True)
            
            # Summary metrics with proper spacing
            st.markdown('<div class="metrics-container">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Inappropriate Prescriptions", len(results['inappropriate_meds']))
            with col2:
                st.metric("Prescription Omissions", len(results['omissions']))
            with col3:
                st.metric("Drug Interactions", len(results['interactions']))
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Add spacing before tabs
            st.markdown("<br><br>", unsafe_allow_html=True)
            
            # Detailed results with better spacing
            st.markdown('<div class="tabs-container">', unsafe_allow_html=True)
            tabs = st.tabs(["Inappropriate Prescriptions", "Prescription Omissions", "Drug Interactions"])
            
            with tabs[0]:
                st.markdown("<br>", unsafe_allow_html=True)
                if results['inappropriate_meds']:
                    for i, med in enumerate(results['inappropriate_meds']):
                        with st.expander(f"🚨 {med['medication']} - {med['age_restriction']} | {med['condition']}"):
                            st.markdown(f"**Rationale:** {med['rationale']}")
                            st.markdown(f"**Reference:** {med['reference']}")
                        if i < len(results['inappropriate_meds']) - 1:
                            st.markdown("<br>", unsafe_allow_html=True)
                else:
                    st.success("✅ No inappropriate prescriptions identified.")
            
            with tabs[1]:
                st.markdown("<br>", unsafe_allow_html=True)
                if results['omissions']:
                    for i, omission in enumerate(results['omissions']):
                        with st.expander(f"⚠️ Missing: {omission['missing_medication']}"):
                            st.markdown(f"**For condition:** {omission['condition']}")
                            st.markdown(f"**Rationale:** {omission['rationale']}")
                            st.markdown(f"**Reference:** {omission['reference']}")
                        if i < len(results['omissions']) - 1:
                            st.markdown("<br>", unsafe_allow_html=True)
                else:
                    st.success("✅ No prescription omissions identified.")
            
            with tabs[2]:
                st.markdown("<br>", unsafe_allow_html=True)
                if results['interactions']:
                    for i, interaction in enumerate(results['interactions']):
                        severity_emoji = "🔴" if interaction['severity'] == "Major" else "🟡" if interaction['severity'] == "Moderate" else "🔵"
                        with st.expander(f"{severity_emoji} {interaction['drug1']} ↔ {interaction['drug2']} | {interaction['severity']} Interaction"):
                            st.markdown(f"**Mechanism:** {interaction['mechanism']}")
                            st.markdown(f"**Clinical Management:** {interaction['management']}")
                            if 'clinical_significance' in interaction:
                                st.markdown(f"**Clinical Significance:** {interaction['clinical_significance']}")
                            st.markdown(f"**Reference:** {interaction['reference']}")
                            
                            # Add severity-based styling
                            if interaction['severity'] == "Major":
                                st.error("⚠️ **MAJOR INTERACTION** - Immediate clinical attention required")
                            elif interaction['severity'] == "Moderate":
                                st.warning("⚡ **MODERATE INTERACTION** - Close monitoring recommended")
                            else:
                                st.info("👁️ **MONITOR** - Watch for potential effects")
                        
                        if i < len(results['interactions']) - 1:
                            st.markdown("<br>", unsafe_allow_html=True)
                else:
                    st.success("✅ No drug interactions identified.")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Download PDF report with better spacing and styling
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown('<div class="download-section">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                pdf_buffer = generate_pdf_report(
                    results['patient_age'],
                    results['indication'],
                    results['medications'],
                    results['inappropriate_meds'],
                    results['omissions'],
                    results['interactions']
                )
                
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_buffer.getvalue(),
                    file_name=f"PediaSafeAI_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.button("🔄 New Screening", type="secondary", use_container_width=True):
                    st.session_state.screening_done = False
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Footer
        st.markdown("""
        <div class="footer">
            <p><strong>Developed for pediatric medication safety • Always consult healthcare professionals for clinical decisions</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Centered Disclaimer
        st.markdown('<div class="disclaimer-container">', unsafe_allow_html=True)
        with st.expander("⚠️ Disclaimer"):
            st.markdown("""
            <div class="disclaimer-content">
                <p><strong>Important Medical Disclaimer:</strong></p>
                <ul>
                    <li>This tool is for educational and screening purposes only</li>
                    <li>It does not replace clinical judgment or professional medical advice</li>
                    <li>Always consult with qualified healthcare professionals before making treatment decisions</li>
                    <li>The databases and criteria used may not be exhaustive</li>
                    <li>Individual patient factors must always be considered</li>
                    <li>This application integrates POPI, PIPc, and KIDs list criteria for comprehensive screening</li>
                    <li>Drug interaction data is sourced from established pharmaceutical databases</li>
                </ul>
                <p><em>Developed for pediatric medication safety • Always consult healthcare professionals for clinical decisions</em></p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def check_age_restriction(restriction, age_in_years):
    """Helper function to check age restrictions"""
    if "< 18 years" in restriction and age_in_years < 18:
        return True
    elif "< 16 years" in restriction and age_in_years < 16:
        return True
    elif "< 12 years" in restriction and age_in_years < 12:
        return True
    elif "< 8 years" in restriction and age_in_years < 8:
        return True
    elif "< 4 years" in restriction and age_in_years < 4:
        return True
    elif "< 2 years" in restriction and age_in_years < 2:
        return True
    elif "< 2 weeks" in restriction and age_in_years < (2/52):
        return True
    elif "< 6 months" in restriction and age_in_years < 0.5:
        return True
    elif "< 1 year" in restriction and age_in_years < 1:
        return True
    return False

if __name__ == "__main__":
    main()
