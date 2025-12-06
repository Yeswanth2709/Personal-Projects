"""
Demo Data Generator - Creates sample patient scenarios for testing
"""

from models import Patient

def get_demo_patients():
    """Return a dictionary of demo patient scenarios."""
    
    patients = {
        "High Risk Elderly": Patient(
            patient_id="DEMO-001",
            age=72,
            sex="Male",
            weight=78.0,
            height=175.0,
            allergies=["penicillin", "sulfa"],
            diagnoses=["heart failure", "kidney disease", "diabetes"],
            current_medications=[
                "warfarin",
                "ibuprofen",
                "metformin",
                "lisinopril",
                "spironolactone"
            ],
            pregnancy_status=False,
            renal_impairment=True,
            hepatic_impairment=False
        ),
        
        "Moderate Risk Adult": Patient(
            patient_id="DEMO-002",
            age=45,
            sex="Female",
            weight=65.0,
            height=165.0,
            allergies=["aspirin"],
            diagnoses=["hypertension", "asthma"],
            current_medications=[
                "lisinopril",
                "levothyroxine",
                "calcium"
            ],
            pregnancy_status=False,
            renal_impairment=False,
            hepatic_impairment=False
        ),
        
        "Low Risk Young": Patient(
            patient_id="DEMO-003",
            age=28,
            sex="Female",
            weight=58.0,
            height=160.0,
            allergies=[],
            diagnoses=[],
            current_medications=[
                "levothyroxine"
            ],
            pregnancy_status=True,
            renal_impairment=False,
            hepatic_impairment=False
        ),
        
        "Complex Polypharmacy": Patient(
            patient_id="DEMO-004",
            age=68,
            sex="Male",
            weight=92.0,
            height=180.0,
            allergies=["penicillin"],
            diagnoses=["diabetes", "hypertension", "heart failure"],
            current_medications=[
                "metformin",
                "simvastatin",
                "clarithromycin",
                "digoxin",
                "furosemide",
                "clopidogrel",
                "omeprazole"
            ],
            pregnancy_status=False,
            renal_impairment=False,
            hepatic_impairment=True
        ),
    }
    
    return patients


def get_demo_questions():
    """Return a list of sample clinical questions."""
    
    questions = [
        "What are the monitoring requirements for warfarin therapy?",
        "How should I manage hypertension in elderly patients?",
        "What are the contraindications for NSAIDs?",
        "What is the first-line treatment for type 2 diabetes?",
        "How do I adjust medications for patients with renal impairment?",
        "What are the drug interactions with warfarin?",
        "What antibiotics are safe in penicillin allergy?",
        "How should I manage heart failure exacerbation?",
        "What are the signs of digoxin toxicity?",
        "What pain management options are available for chronic kidney disease?"
    ]
    
    return questions


def print_demo_scenarios():
    """Print demo patient scenarios for reference."""
    patients = get_demo_patients()
    
    print("=" * 80)
    print("DEMO PATIENT SCENARIOS")
    print("=" * 80)
    print()
    
    for name, patient in patients.items():
        print(f"📋 {name}")
        print(f"   ID: {patient.patient_id}")
        print(f"   Age: {patient.age} | Sex: {patient.sex}")
        print(f"   Medications: {len(patient.current_medications)}")
        if patient.allergies:
            print(f"   Allergies: {', '.join(patient.allergies)}")
        if patient.diagnoses:
            print(f"   Conditions: {', '.join(patient.diagnoses)}")
        if patient.renal_impairment:
            print(f"   ⚠️ Renal Impairment")
        if patient.hepatic_impairment:
            print(f"   ⚠️ Hepatic Impairment")
        if patient.pregnancy_status:
            print(f"   ⚠️ Pregnancy")
        print()
    
    print("=" * 80)
    print("SAMPLE CLINICAL QUESTIONS")
    print("=" * 80)
    print()
    
    questions = get_demo_questions()
    for i, q in enumerate(questions, 1):
        print(f"{i}. {q}")
    print()


if __name__ == "__main__":
    print_demo_scenarios()
